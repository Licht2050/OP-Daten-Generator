import asyncio
import datetime
import json
import os
import sys
import uuid
from typing import Callable, Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process


# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
from confluent_kafka import Consumer
from paths_config import (
    CONFIG_FILE_PATH, POLL_TIMEOUT, 
    VITAL_PARAMS_TABLE_DEFFINATION_PATH
)
from base import Base
from cql_loader import CQLLoader
from cassandra_connector import CassandraConnector
from config_loader import ConfigLoader
from middelware_manager import MiddlewareManager
from process_vital_parameters import TimSynchronization, VitalsChecker
from graphql_pub import GraphQLVitalParamPub


class KafkaToCassandra(Base):
    """Class to consume data from Kafka and store it into Cassandra database."""

    def __init__(self, config: Dict[str, Any], schema_commands: Optional[List[str]]=None):
        """Initialize Kafka consumer and Cassandra session.

        Args:
            config (dict): Configuration settings.
            schema_commands (list, optional): Schema commands to ensure table exists.
        """
        super().__init__()
        self.config: Dict[str, Any] = config
        self.vital_parameters_config = self.config['topics']['vital_parameters']
        self._setup_services()
        self.middleware_manager = MiddlewareManager()
        if schema_commands:
            self.ensure_table_exists(schema_commands)
        self._setup_logging()
        self.executor = ThreadPoolExecutor(max_workers=self.config['threads']['max_workers'])  

    def _setup_services(self) -> None:
        """Initialize all services"""
        self.kafka_config = self._get_kafka_config()
        self.consumer = self._init_consumer()
        self.cassandra_session, self.cassandra_connector = self._init_cassandra_session()

    def _get_kafka_config(self) -> Dict[str, str]:
        """Return Kafka configuration."""
        return {
            'bootstrap.servers': self.vital_parameters_config['bootstrap_servers'],
            'group.id': self.vital_parameters_config['group_id'],
            'auto.offset.reset': 'latest'
        }
    
    def _init_cassandra_session(self) -> Tuple[Any, Any]:
        """Initialize and return Cassandra session and connector."""
        cassandra_connector = CassandraConnector(self.config['cassandra']['nodes'])
        session = cassandra_connector.connect(self.config['cassandra']['keyspace'])
        return session, cassandra_connector

    def ensure_table_exists(self, schema_commands: List[str]) -> None:
        """Ensure that tables are created in Cassandra."""
        for command in schema_commands:
            self.cassandra_connector.connect(self.config['cassandra']['keyspace'], command)


    def _init_consumer(self) -> Consumer:
        """Initialize and return Kafka consumer."""
        return Consumer(self.kafka_config)


    def save_to_cassandra(self, processed_message: Any) -> None:
        """Save the consumed message into Cassandra database."""
        try:
            message_dict = processed_message.raw_message
            # self.logger.info(f"Saving message to Cassandra: {message_dict}")
            source, value, timestamp, patient_id, bucket_date = self.extract_message_details(message_dict)
            query_params = self.create_query_params(source, value, timestamp, patient_id, bucket_date, processed_message)
            query = self.construct_query(source, value, query_params)
            self.cassandra_session.execute(query, query_params)
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            self._handle_exception(e)


    def extract_message_details(self, message_dict: Dict[str, Any]) -> Tuple:
        """
        Extracts the message details from the message dictionary.

        Parameters:
            message_dict (dict): The message dictionary.

        Returns:
            tuple: The message details.
        """
        source = message_dict['source']
        value = message_dict['value']
        timestamp = message_dict['timestamp']
        patient_id = uuid.UUID(value.get('Patient_ID'))
        bucket_date = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').date()
        return source, value, timestamp, patient_id, bucket_date

    def create_query_params(self, source: str, value: Dict[str, Any], timestamp: str, patient_id: uuid.UUID, bucket_date: datetime.date, processed_message: Any) -> Dict[str, Any]:
        """
        Creates the query parameters for the Cassandra query based on the source and message details.

        Parameters:
            source (str): The source of the message data.
            value (dict): The value data from the message.
            timestamp (str): The timestamp of the message.
            patient_id (uuid.UUID): The UUID of the patient.
            bucket_date (datetime.date): The bucket date for the data.
            processed_message (any): The processed message object.

        Returns:
            dict: The query parameters for the Cassandra query.
        """
        status = processed_message.get_data('status')
        estimated_time = processed_message.get_data('estimated_time')
        query_params = {
            'Patient_ID': patient_id,
            'bucket_date': bucket_date,
            'timestamp': timestamp,
            'status': status,
            'value': value.get(source),
        }
        if source in ['blood_pressure', 'heart_rate']:
            query_params['estimated_time'] = estimated_time
        return query_params

    def construct_query(self, source: str, value: Dict[str, Any], query_params: Dict[str, Any]) -> str:
        """
        Constructs the Cassandra query based on the source and message details.

        Parameters:
            source (str): The source of the message data.
            value (dict): The value data from the message.
            query_params (dict): The query parameters for the Cassandra query.

        Returns:
            str: The Cassandra query.
        """
        query_map = {
            'blood_pressure': """INSERT INTO {source} (Patient_ID, bucket_date, timestamp, estimated_time, systolic, diastolic, status) VALUES (%(Patient_ID)s, %(bucket_date)s, %(timestamp)s, %(estimated_time)s, %(systolic)s, %(diastolic)s, %(status)s)""",
            'heart_rate': """INSERT INTO {source} (Patient_ID, bucket_date, timestamp, estimated_time, {source}, status) VALUES (%(Patient_ID)s, %(bucket_date)s, %(timestamp)s, %(estimated_time)s, %(value)s, %(status)s)""",
            'default': """INSERT INTO {source} (Patient_ID, bucket_date, timestamp, {source}, status) VALUES (%(Patient_ID)s, %(bucket_date)s, %(timestamp)s, %(value)s, %(status)s)""",
        }
        if source == 'blood_pressure':
            query_params['systolic'] = value.get('systolic')
            query_params['diastolic'] = value.get('diastolic')
        query = query_map.get(source, query_map['default']).format(source=source)
        return query


    def consume_and_store(self) -> None:
        """Consume messages from Kafka and store them into Cassandra."""
        while True:
            message = self.consumer.poll(POLL_TIMEOUT)
            if message is None:
                continue
            if message.error():
                self._handle_exception(f"Error while consuming message: {message.error()}")
            else:
                # processed_message = self.process_middlewares(message)
                # self.save_to_cassandra(processed_message)
                # consum message in a thread
                decoded_msg = self._decode_message(message)
                self.executor.submit(self.process_and_save_message, decoded_msg)


    def process_and_save_message(self, message: Any) -> None:
        """Process a single message and save it to Cassandra."""
        try:
            processed_message = self.process_middlewares(message)
            self.save_to_cassandra(processed_message)
        except Exception as e:
            self._handle_exception(e)

    def add_middleware(self, middleware_fn: Callable) -> None:
        """Add middleware function."""
        self.middleware_manager.add_middleware(middleware_fn)

    def process_middlewares(self, message: Any) -> Any:
        """Process middleware functions on message."""
        return self.middleware_manager.process_middlewares(message)


    def close_connections(self) -> None:
        """Close all connections."""
        self.consumer.close()
        self.cassandra_session.shutdown()

    def run(self) -> None:
        """Run the Kafka consumer."""
        #print("Some debug output...", flush=True)
        self.consumer.subscribe([self.vital_parameters_config['topic_name']])
        self.consume_and_store()
    

if __name__ == '__main__':
    connector = None
    graphql_publisher = None

    try:
        # Load configuration
        config_loader = ConfigLoader(CONFIG_FILE_PATH)
        config = config_loader.get_all_configs() 
        
        # Load CQL table definition
        cql_loader = CQLLoader(VITAL_PARAMS_TABLE_DEFFINATION_PATH)
        table_definition = cql_loader.get_commands(category="Schema")

        # Initialize main connector
        connector = KafkaToCassandra(config, table_definition)

        # Initialize middlewares
        checker = VitalsChecker(config['thresholds'])
        sync_config_loader = ConfigLoader("../config/config.json")
        synchroneizer = TimSynchronization(sync_config_loader.load_config("synchronization"))



        pub_sub_config = config.get("publish_subscribe_channels")
        graphql_publisher = GraphQLVitalParamPub(pub_sub_config)
        # loop.run_until_complete(graphql_publisher.initialize())
        graphql_publisher.event_loop.run_until_complete(graphql_publisher.initialize())
        # Add middlewares
        connector.add_middleware(checker.check_vitals)
        connector.add_middleware(synchroneizer.synchronize)
        connector.add_middleware(graphql_publisher.process_data)


        # Run the connector
        connector.run()
    
    except KeyboardInterrupt:
        print("Interrupted by user. Closing connections...")
    finally:
        if connector:
            connector.close_connections()
        if graphql_publisher:
            print("Closing graphql publisher...")
            graphql_publisher.event_loop.run_until_complete(graphql_publisher.close())
            graphql_publisher.event_loop.close() 

