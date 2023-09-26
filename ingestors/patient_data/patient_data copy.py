import json
import os
import sys
from threading import Lock
import traceback
from typing import Any, Dict





sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/mongodb')))

from db_schema import Address, HolidayRecord, IllnessRecord, Patient
from base import Base
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager import MiddlewareManager
from process_patient_data import DataProcessor
from mongodb_conncetor import MongoDBConnector




class PatientDataHandler(Base):
    def __init__(self, patient_data_config: Dict[str, Any], mongodb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()
        self._setup_logging()
        self.patient_data_config = patient_data_config
        self.mongodb_config = mongodb_config
        self.max_workers = max_workers
        self.middleware_manager = MiddlewareManager()
        self._start_consumer()
        self.lock = Lock()

    def _start_consumer(self) -> None:
        """
        Start the kafka consumer
        """
        self.logger.info("Starting patient data consumer")
        self.consumer = KafkaTopicConsumer(self.patient_data_config, callback=self.process_and_save_data)
        
    def add_middleware(self, middleware_fn):
        self.middleware_manager.add_middleware(middleware_fn)
    
    
    def get_patient_data(self, processed_data):
        """Get patient data from processed data."""
        patient_id = processed_data['value'].get('Patient_ID')
        if processed_data['source'] == 'patient_records':
            # Build the Address from the individual fields
            address_data = {}
            for field in ['Straße', 'Stadt', 'Postleitzahl']:
                if field in processed_data['value']:
                    address_data[field] = processed_data['value'].pop(field)
            print(f"address_data: {address_data}")
            patient_data = Patient(**processed_data['value'])
            # Create an Address object if any address field is present
            if address_data:
                patient_data.address = Address(**address_data)
            
        else:
            # Create a patient data with only the patient ID, and no other fields
            data = {"Patient_ID": patient_id}
            for field in Patient.__annotations__.keys():
                if field in processed_data['value']:
                    data[field] = processed_data['value'][field]
            patient_data = Patient(**data)
        return patient_data, patient_id
    
    def get_record(self, record_class, processed_data):
        """Get record instance from the processed data."""
        return record_class(**processed_data['value'])

    def get_update_data(self, processed_data, patient_dict):
        """Get the update data for MongoDB update operation."""
        source_to_class_map = {
            'illness_records': IllnessRecord,
            'holiday_records': HolidayRecord,
        }
        source_to_field_map = {
            'illness_records': 'illness_records',
            'holiday_records': 'holiday_records',
        }
        
        if processed_data['source'] in source_to_class_map:
            record_class = source_to_class_map[processed_data['source']]
            field = source_to_field_map[processed_data['source']]
            record = self.get_record(record_class, processed_data)
            update_data = {"$push": {field: record.model_dump(by_alias=False)}}
        else:
            non_null_fields = {k: v for k, v in patient_dict.items() if v is not None}
            # Remove the illness and holiday records fields to prevent overwriting existing records
            non_null_fields.pop('illness_records', None)
            non_null_fields.pop('holiday_records', None)
            update_data = {"$set": non_null_fields}
        return update_data

    def process_and_save_data(self, data: Dict[str, Any]) -> None:
        client = None
        try:
            self.logger.info("Processing and saving patient data")
            processed_data = self.middleware_manager.process_middlewares(data).to_dict()
            print(f"processed_data-------------------- inside---------: {processed_data}")
            mongo_connector = MongoDBConnector(
                host=self.mongodb_config['host'],
                port=self.mongodb_config['port'],
                database_name=self.mongodb_config['database'],
                collection_name=self.mongodb_config['collection'],
            )
            client = mongo_connector.connect()
            db = client[self.mongodb_config['database']]
            collection = db[self.mongodb_config['collection']]
            
            patient_data, patient_id = self.get_patient_data(processed_data)
            patient_dict = patient_data.model_dump(by_alias=False)
            
            if processed_data['source'] in ['illness_records', 'holiday_records']:
                record_class = IllnessRecord if processed_data['source'] == 'illness_records' else HolidayRecord
                record = record_class(**processed_data['value'])
                patient_dict[f'{processed_data["source"][:-1]}s'] = [record.model_dump(by_alias=False)]
            print(f"patient_dict++++++++++++++++++++++++++++++++++++++++++: {patient_dict}")
            with self.lock:
                existing_record = collection.find_one({"patient_id": patient_id})
                if existing_record:
                    update_data = self.get_update_data(processed_data, patient_dict)
                    collection.update_one({"patient_id": patient_id}, update_data)
                else:
                    collection.insert_one(patient_dict)
        # except KeyboardInterrupt:
        #     self.logger.info("Interrupted by user. Closing connections...")
        #     if client:
        #         client.close()
                
        except Exception as e:
            self._handle_exception(f"Error while processing and saving data: {e}")
            print(traceback.format_exc())
            raise


    def run(self) -> None:
        """
        Run the patient data handler
        """
        self.logger.info("Starting patient data handler")
        self.consumer.consume()



if __name__ == "__main__":
    # Load the configuration
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs()
    patient_data_config = config['topics']['patient_data']
    mangodb_config = config['mongodb']
    max_workers = config.get("threads", {}).get("max_workers", 10)

    data_processor = DataProcessor()

    # Start the staff communication handler
    patient_data_handler = PatientDataHandler(patient_data_config, mangodb_config, max_workers=max_workers)
    patient_data_handler.add_middleware(data_processor.process_data)
    patient_data_handler.run()
