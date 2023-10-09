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
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/mongodb'))
])

from db_schema import OpDetails, Patient, PostOPRecord, PreOPRecord
from base import Base
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager import MiddlewareManager
from process_op_records import DataProcessor
from mongodb_conncetor import MongoDBConnector



class OpRecordHandler(Base):
    """A class to handle operations related to the operation team."""
    def __init__(self, op_record_config: Dict[str, Any], mongodb_config: Dict[str, Any], max_workers: int =10) -> None:
        super().__init__()
        self._setup_logging()
        self.op_record_config = op_record_config
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
                config=self.op_record_config,
                callback=self._process_and_save_message,
                max_workers=self.max_workers
            )
            
            self.op_team_consumer = KafkaTopicConsumer(
                config=self.op_record_config,
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
            
            processed_message = self.process_middleware(message)
            # self.logger.info(f"Processed message: {processed_message}")
            
            self.logger.info(f"Received message: {message}")

            source = processed_message['source']
            patient_id = processed_message.get('patient_id')
            if not patient_id:
                self.logger.warning("No patient ID found")
                return
            
            record = processed_message.get('value')
            if not isinstance(record, BaseModel):
                self.logger.warning("No valid record data found to save")
                return
        
            
            with self.lock:
                self._update_or_insert_data(source, patient_id, record)

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

    def _update_or_insert_data(self, source: str, patient_id: str, record) -> None:
        """Update existing data or insert new data in the database."""
        existing_op_details = self.mongo_connector.find_data({"patient_id": patient_id})
        if existing_op_details:
            self._update_existing_data(source, record, existing_op_details, patient_id)
        else:
            

            
            record_dict = record.model_dump(by_alias=True)
            # if source == 'pre_op_record':
            #     op_details = OpDetails(patient_id=patient_id, Pre_OP_Record=PreOPRecord.model_validate(record_dict), Post_OP_Record=None)
            # elif source == 'post_op_record':
            #     op_details = OpDetails(patient_id=patient_id, Pre_OP_Record=None, Post_OP_Record=PostOPRecord.model_validate(record_dict))
            # else:
            #     self.logger.error(f"Unknown source: {source}")
            #     return            

            # print(f"operation_record: {op_details}")
            
            new_op_details = {"patient_id": patient_id, source: [record_dict]}
            self.mongo_connector.insert_data(new_op_details)

    def _update_existing_data(self, source: str, record, existing_patient: Dict[str, Any], patient_id: str) -> None:
        """Update existing data in the database."""

        record_dict = record.model_dump(by_alias=False)
        
        update_data = {"$set": {source: record_dict}}   
        
        self.mongo_connector.update_data({"patient_id": patient_id}, update_data, update_many=False)



    def run(self) -> None:
        self.patient_consumer.consume()


if __name__ == '__main__':
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs()
    op_record_config = config['topics']['op_record']
    mongodb_config = config['op_details']
    operation_team_handler = OpRecordHandler(op_record_config, mongodb_config)

    data_processor = DataProcessor()

    operation_team_handler.add_middleware(data_processor.process_data)
    operation_team_handler.run()
    


