import sys
import os
from threading import Lock
import traceback
from typing import Any, Dict

from pydantic import BaseModel

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../config'),
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../helper'),
    os.path.join(os.path.dirname(__file__), '../db_connectors'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb'))
])

from base import Base
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager import MiddlewareManager
from process_operation_team import DataProcessor
from mongodb_conncetor import MongoDBConnector



class OperationTeamHandler(Base):
    """A class to handle operations related to the operation team."""
    def __init__(self, operation_team_config: Dict[str, Any], mongodb_config: Dict[str, Any], max_workers: int =10) -> None:
        super().__init__()
        self._setup_logging()
        self.operation_team_config = operation_team_config
        self.mongodb_config = mongodb_config
        self.max_workers = max_workers
        self.middleware_manager = MiddlewareManager()
        self.lock = Lock()
        self._start_consumer()
        self.initialize_mongodb_connector()

    def initialize_mongodb_connector(self) -> None:
        # Initialize MongoDBConnector
        try:
            self.mongo_connector = MongoDBConnector(
                host=self.mongodb_config['host'],
                port=self.mongodb_config['port'],
                database_name=self.mongodb_config['database'],
                collection_name=self.mongodb_config['collection']
            )
        except Exception as e:
            self._handle_exception(f"Error initializing MongoDB connector: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _start_consumer(self) -> None:
        """Initialize and start the Kafka consumer."""
        try:
            self.patient_consumer = KafkaTopicConsumer(
                config=self.operation_team_config,
                callback=self._process_and_save_message,
                max_workers=self.max_workers
            )
            
            self.op_team_consumer = KafkaTopicConsumer(
                config=self.operation_team_config,
                callback=self._process_and_save_message,
                max_workers=self.max_workers
            )

        except Exception as e:
            self._handle_exception(f"Error starting Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def add_middleware(self, middleware: Any) -> None:
        """Add a middleware to the middleware manager."""
        self.middleware_manager.add_middleware(middleware)
    
    def process_middleware(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process the message through the middleware manager."""
        return self.middleware_manager.process_middlewares(message).to_dict()

    def _process_and_save_message(self, message: Dict[str, Any]) -> None:
        """Process and save the message in the database."""
        try:
            self.logger.info(f"Received message: {message}")
            processed_message = self.process_middleware(message)
            # self.logger.info(f"Processed message: {processed_message}")
            
            source = processed_message['source']
            patient_id = processed_message.get('patient_id')
            if not patient_id:
                self.logger.warning("No patient ID found")
                return
            
            record = processed_message.get('value')
            if not isinstance(record, BaseModel):
                self.logger.warning("No valid record data found to save")
                return
        
            record_dict = record.model_dump(by_alias=False)
            with self.lock:
                self._update_or_insert_data(source, patient_id, record_dict)

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user. Closing connections...")
            self.lock.release()
            self.patient_consumer.close()
            
        except Exception as e:
            self._handle_exception(f"Error processing message: {e}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            self.lock.release()

    def _update_or_insert_data(self, source: str, patient_id: str, record_dict: Dict[str, Any]) -> None:
        """Update existing data or insert new data in the database."""
        existing_op_details = self.mongo_connector.find_data({"patient_id": patient_id})
        if existing_op_details:
            self._update_existing_data(source, record_dict, existing_op_details, patient_id)
        else:
            new_op_details = {"patient_id": patient_id, source: [record_dict]}
            self.mongo_connector.insert_data(new_op_details)

    def _update_existing_data(self, source: str, record_dict: Dict[str, Any], existing_op_details: Dict[str, Any], patient_id: str) -> None:
        """Update existing data in the database."""
        
        # if existing_op_details.get(source) is None:
            # The field is not set in the existing document, so we set it to an array containing the new record
        update_data = {"$set": {source: [record_dict]}}
        # else:
        #     # The field is already an array in the existing document, so we push the new record to it
        #     # Get the existing op_team array
        #     op_team = existing_op_details.get('op_team')
        #     if op_team:
        #         # Iterate over the existing op_team array and update the individual role arrays
        #         for team in op_team:
        #             for role, members in record_dict.items():
        #                 # Here role will be 'doctors', 'nurses', or 'anesthetists'
        #                 # and members will be the array of members for that role in the new record
        #                 for new_member in members:                                   
        #                     if new_member not in team[role]:
        #                         team[role].append(new_member)
        #     update_data = {"$set": {source: op_team}}
        self.mongo_connector.update_data({"patient_id": patient_id}, update_data, update_many=False)

    def run(self) -> None:
        self.patient_consumer.consume()


if __name__ == '__main__':
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs()
    operation_team_config = config['topics']['operation_team']
    mongodb_config = config['op_details']
    operation_team_handler = OperationTeamHandler(operation_team_config, mongodb_config)

    data_processor = DataProcessor()

    operation_team_handler.add_middleware(data_processor.process_data)
    operation_team_handler.run()
    


