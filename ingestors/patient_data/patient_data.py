
import os
import sys
from threading import Lock
import traceback
from typing import Any, Dict

from pydantic import BaseModel







sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../schema/mongodb'))


from base import Base
from db_schema import Patient
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager import MiddlewareManager
from process_patient_data import DataProcessor
from mongodb_conncetor import MongoDBConnector




class PatientDataHandler(Base):
    SOURCE_TO_FIELD_MAP = {
        'patient_records': '',
        'illness_records': 'illness_records',
        'holiday_records': 'holiday_records',
    }
    def __init__(self, patient_data_config: Dict[str, Any], mongodb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()
        self._setup_logging()
        self.patient_data_config = patient_data_config
        self.mongodb_config = mongodb_config
        self.max_workers = max_workers
        self.middleware_manager = MiddlewareManager()
        self._start_consumer()
        self.lock = Lock()

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
        """
        Start the kafka consumer
        """
        self.logger.info("Starting patient data consumer")
        self.consumer = KafkaTopicConsumer(self.patient_data_config, callback=self.process_and_save_data)
        
    def add_middleware(self, middleware_fn):
        self.middleware_manager.add_middleware(middleware_fn)
    
    def process_middelwares(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.middleware_manager.process_middlewares(data).to_dict()

    def process_and_save_data(self, data: Dict[str, Any]) -> None:
        try:
            self.logger.info("Processing and saving patient data")
            processed_data = self.process_middelwares(data)
            
            if 'source' not in processed_data:
                self.logger.warning("No data source found")
                return

            source = processed_data['source']
            patient_id = processed_data.get('patient_id')
            
            if not patient_id:
                self.logger.warning("No patient ID found")
                return
            
            record = processed_data.get('value')
            if not isinstance(record, BaseModel):
                self.logger.warning("No valid record data found to save")
                return
            
        
            with self.lock:
                existing_patient = self.mongo_connector.find_data({"patient_id": patient_id})
                field_name = self.SOURCE_TO_FIELD_MAP.get(source)

                if existing_patient:
                    record_dict = record.model_dump(by_alias=False)
                    # Update the existing record dynamically based on the source
                    if field_name:  # For illness and holiday records
                        update_data = {"$push": {field_name: record_dict}}
                    else:  # For patient records
                        non_null_fields = {k: v for k, v in record_dict.items() if v is not None and v != []}
                        
                        non_null_fields.pop('illness_records', None)
                        non_null_fields.pop('holiday_records', None)
                        non_null_fields.pop('op_team', None)
                        non_null_fields.pop('operation_records', None)
                        update_data = {"$set": non_null_fields} 
                        print(f"non_null_fields: {update_data}")
                    self.mongo_connector.update_data({"patient_id": patient_id}, update_data, update_many=False)
                else:
                    record_dict = record.model_dump(by_alias=True)
                    # Create a new Patient data with default values
                    new_patient_data_dict = {"Patient_ID": patient_id}
                    
                    # If the source is 'illness_records' or 'holiday_records', add the record to the respective list
                    if field_name:
                        new_patient_data_dict[field_name] = [record_dict]
                    # If the source is 'patient_records', update the new patient data with the record data
                    else:
                        new_patient_data_dict.update(record_dict)

                    # Create a new Patient model instance
                    new_patient_data_model = Patient.model_validate(new_patient_data_dict)
                    
                    # Convert the Patient model instance to a dictionary
                    new_patient_data = new_patient_data_model.model_dump(by_alias=False)

                    # Insert the new patient data into the database
                    self.mongo_connector.insert_data(new_patient_data)

        except KeyboardInterrupt:
            self.logger.info("Interrupted by user. Closing connections...")
            self.consumer.close()
            self.lock.release()
        except DataProcessor.DataProcessingError as e:
            self._handle_exception(f"Data processing error: {e}")
        except Exception as e:
            self._handle_exception(f"Error while processing and saving data: {e}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            self.lock.release()


        
    def _update_exiting_data(self, existing_patient, record, field_name, patient_id):
        record_dict = record.model_dump(by_alias=False)
        # Update the existing record dynamically based on the source
        if field_name:  # For illness and holiday records
            update_data = {"$push": {field_name: record_dict}}
        else:  # For patient records
            non_null_fields = {k: v for k, v in record_dict.items() if v is not None and v != []}
            
            non_null_fields.pop('illness_records', None)
            non_null_fields.pop('holiday_records', None)
            non_null_fields.pop('op_team', None)
            non_null_fields.pop('operation_records', None)
            update_data = {"$set": non_null_fields} 
            print(f"non_null_fields: {update_data}")
        self.mongo_connector.update_data({"patient_id": patient_id}, update_data, update_many=False)

        

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
