import datetime
import json
import logging
import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))


from confluent_kafka import Consumer
from paths_config import (
    CONFIG_FILE_PATH, POLL_TIMEOUT, 
    VITAL_PARAMS_TABLE_DEFFINATION_PATH
)
from cql_loader import CQLLoader
from cassandra_connector import CassandraConnector
from config_loader import ConfigLoader
from processed_message import ProcessedMessage
from process_vital_parameters import VitalsChecker




class KafkaToCassandra:
    """Class to consume data from Kafka and store it into Cassandra database."""

    def __init__(self, config, schema_commands=None):
        """Initialize Kafka consumer and Cassandra session.

        Args:
            config (dict): Configuration settings.
            schema_commands (list, optional): Schema commands to ensure table exists.
        """
        self.config = config
        self._setup_services()
        self.middlewares = []
        if schema_commands:
            self.ensure_table_exists(schema_commands)
        self._setup_logging()

    def _setup_services(self):
        """Initialize all services"""
        self.kafka_config = self._get_kafka_config()
        self.consumer = self._init_consumer()
        self.cassandra_session, self.cassandra_connector = self._init_cassandra_session()

    def _setup_logging(self):
        """Initialize logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _get_kafka_config(self):
        """Return Kafka configuration."""
        return {
            'bootstrap.servers': self.config['kafka']['bootstrap_servers'],
            'group.id': self.config['kafka']['group_id'],
            'auto.offset.reset': 'latest'
        }
    
    def _init_cassandra_session(self):
        """Initialize and return Cassandra session and connector."""
        cassandra_connector = CassandraConnector(self.config['cassandra']['nodes'])
        session = cassandra_connector.connect(self.config['cassandra']['keyspace'])
        return session, cassandra_connector

    def ensure_table_exists(self, schema_commands):
        """Ensure that tables are created in Cassandra.

        Args:
            schema_commands (list): List of schema commands to create tables.
        """
        for command in schema_commands:
            self.cassandra_connector.connect(self.config['cassandra']['keyspace'], command)


    def _init_consumer(self):
        """Initialize and return Kafka consumer."""
        return Consumer(self.kafka_config)

    def add_middleware(self, middleware_fn):
        """Add middleware function.

        Args:
            middleware_fn (function): Middleware function to process messages.
        """
        self.middlewares.append(middleware_fn)

    def process_middlewares(self, message):
        """Process middleware functions on message.

        Args:
            message (message): Message to be processed.

        Returns:
            message: Processed message.
        """
        processed_message = ProcessedMessage(message)
        for middleware in self.middlewares:
            middleware(processed_message)
        return processed_message

    

    def save_to_cassandra(self, processed_message):
        """Save the consumed message into Cassandra database.

        Args:
            message (message): Message to be saved.
        """
        try:
            message = processed_message.raw_message
            message_dict = json.loads(message.value().decode('utf-8'))
            source = message_dict['source']
            value = message_dict['value']
            timestamp = message_dict['timestamp']
            patient_id = uuid.UUID(value.get('Patient_ID'))
            bucket_date = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').date()

            status = processed_message.get_data('status') 

            if source == 'blood_pressure':
                query = f"""
                INSERT INTO {source} (Patient_ID, bucket_date, timestamp, systolic, diastolic, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cassandra_session.execute(query, (patient_id, bucket_date, timestamp, value.get('systolic'), value.get('diastolic'), status))

            else:
                query = f"""
                INSERT INTO {source} (Patient_ID, bucket_date, timestamp, {source}, status)
                VALUES (%s, %s, %s, %s, %s)
                """
                self.cassandra_session.execute(query, (patient_id, bucket_date, timestamp, value.get(source), status))

        except(json.JSONDecodeError, AttributeError, KeyError) as e:
            self.logger.error(f"Could not save message to Cassandra: {e}")

    def consume_and_store(self):
        while True:
            message = self.consumer.poll(POLL_TIMEOUT)
            if message is None:
                continue
            if message.error():
                self.logger.error(f"Error while consuming message: {message.error()}")
            else:
                processed_message = self.process_middlewares(message)
                self.save_to_cassandra(processed_message)

    def close_connections(self):
        self.consumer.close()
        self.cassandra_session.shutdown()

    def run(self):
        try:
            self.consumer.subscribe([self.config['kafka']['topic']])
            self.consume_and_store()
        except KeyboardInterrupt:
            self.logger.info("Operation stopped by the user")
        finally:
            self.close_connections()

if __name__ == '__main__':
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs() 
    cql_loader = CQLLoader(VITAL_PARAMS_TABLE_DEFFINATION_PATH)
    table_definition = cql_loader.get_commands(category="Schema")
    connector = KafkaToCassandra(config, table_definition)

    checker = VitalsChecker(config['thresholds'])


    connector.add_middleware(checker.check_vitals)
    connector.run()
    

