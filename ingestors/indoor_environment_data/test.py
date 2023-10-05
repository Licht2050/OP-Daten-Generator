import os
import sys
import threading
from kafka import KafkaConsumer
import json

from pydantic import ValidationError

from confluent_kafka import Consumer, KafkaError

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../config'),
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb')),
    os.path.join(os.path.dirname(__file__), '../helper'),
    os.path.join(os.path.dirname(__file__), '../db_connectors')
])


from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from mongodb_conncetor import MongoDBConnector
from kafka_consumer import KafkaTopicConsumer
from influxdb_connector import InfluxDBConnector
from typing import Dict, Any
from indoor_environment_data_schema import IndoorEnvironmentDataStatus, IndoorEnvironmentDataValue
import traceback
from base import Base


class DataProcessor(Base):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__()
        self._setup_logging()
        self.patient_entry_exit_events_config = patient_entry_exit_events_config
        self.max_workers = max_workers
        self.mongodb_config = mongodb_config
        self._initialize_influxdb_connector(influxdb_config)
        self._initialize_mongodb_connector(mongodb_config)
        self._start_consumer()
        self.current_patients = {}
        self.current_patient_id = None
        self.patients_locks = threading.Lock()
        self._stop_request = False

        self._stop_event = threading.Event()
        self.check = False

    def _start_consumer(self) -> None:
        """Initialize and start the Kafka consumer."""
        try:
            conf = {
                'bootstrap.servers': self.patient_entry_exit_events_config['bootstrap_servers'],
                'group.id': self.patient_entry_exit_events_config['group_id'],
                'auto.offset.reset': 'earliest',
                
            }

            self.consumer = Consumer(conf)
            self.consumer.subscribe([self.patient_entry_exit_events_config['topic_name']])

        except Exception as e:
            self._handle_exception(f"Error starting Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
            raise

        
    def run(self):
        try:
            print("Running Kafka consumer==============================")
            while not self._stop_event.is_set():
                message = self.consumer.poll(1.0)  # 1.0 is the timeout in seconds
                if message is None:
                    continue
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        print(f"Reached end of topic {message.topic()} partition {message.partition()} at offset {message.offset()}")
                    else:
                        print(f"Error while consuming message: {message.error()}")
                else:
                    value = json.loads(message.value().decode('utf-8'))
                    self._process_message(value)
        except KeyboardInterrupt:
            print("Consumer interrupted by user.")
        finally:
            self.stop()
            print("Closing Kafka consumer==============================")

    def _initialize_mongodb_connector(self, mongodb_config: Dict[str, Any]):
        self.mongodb_connector = MongoDBConnector(
            host=self.mongodb_config['host'],
            port=self.mongodb_config['port'],
            database_name=self.mongodb_config['database'],
            collection_name=self.mongodb_config['collection']
        )

    def fetch_patient_op_room(self, patient_id):
        try:
            patient = self.mongodb_connector.find_data({'patient_id': patient_id})
            if patient and 'operation_records' in patient and 'pre_op_record' in patient['operation_records']:
                print(f"Patinet {patient}")
                return patient['operation_records']['pre_op_record'].get('operation_room')
        except Exception as e:
            self.logger.error(f"Error fetching operation room for patient {patient_id}: {e}")
            return None

    
    
    def _process_message(self, message):
        
        value = message.get("value")
        print(f"Value-----------------: {value}")
        patient_id = value.get("Patient_ID")
        print(f"Patient ID-----------------: {patient_id}")
        with self.patients_locks:
            if value.get("event_type") == "patient_entered":
                op_room = self.fetch_patient_op_room(patient_id)
                self.current_patients[patient_id] = op_room
            elif value.get("event_type") == "patient_left":
                del self.current_patients[patient_id]
    
    def _initialize_influxdb_connector(self, influxdb_config: Dict[str, Any] ) -> None:
        """Initialize the InfluxDB connector."""
        try:
            self.influxdb_connector = InfluxDBConnector(**influxdb_config)
        except Exception as e:
            self._handle_exception(f"Error initializing InfluxDB connector: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def create_indoor_environment_schema(self, processed_message, patient_id):
        timestamp_str = processed_message.get("timestamp")
        timestamp = self._convert_timestamp(timestamp_str) if timestamp_str else self._get_current_timestamp()

        value_data = processed_message.get("value", {})


        indoor_environment_value = value_data.model_dump(by_alias=False)
        source = patient_id + "_indoor_environment_data"
        fields = {key: value for key, value in indoor_environment_value.items() if key != "op_room"}

        schema = {
            "measurement": source,
            "tags": {
                "patient_id": patient_id,
                "op_room": indoor_environment_value.get("op_room"),
            },
            "time": timestamp,
            "fields": fields
        }
        return schema


        
    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message
        value = data.get('value')
        try:
            # print(f"Processing data: {data.raw_message}")
            self.validate_data(data)

            indoor_environment_value = IndoorEnvironmentDataValue(**value)
            processed_message.add_data('value', indoor_environment_value)
            
            print(f"Processed message------------------: {processed_message.to_dict()}")
            print(f"Current patients+++++++++++++++++++++++++++++++++++ {self.current_patients}")
            # if self.current_patients:
            #     for patient_id, op_room in self.current_patients.items():
            #         if op_room == indoor_environment_value.op_room:
            #             schema = self.create_indoor_environment_schema(processed_message.to_dict(), patient_id) 
            #             self.influxdb_connector.write_points([schema])
                        

        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def validate_data(self, data):
        """Validate data before writing to database """
        try:
            IndoorEnvironmentDataStatus(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def stop(self):  # Neue Methode, um das Herunterfahren zu initiieren
        self.logger.info("============================================================Stopping Kafka consumer...")
        self._stop_event.set()
        self.consumer.close()
        self.mongodb_connector.close()
        self.influxdb_connector.close()



if __name__ == "__main__":
    data_processor = None
    try:
        config_loader = ConfigLoader(CONFIG_FILE_PATH)
        config = config_loader.get_all_configs()
        indoor_environment_config = config.get("topics", {}).get("indoor_environment_data")
        mongodb_config = config.get("mongodb")
        patient_entry_exit_events_config = config.get("topics", {}).get("patient_entry_exit_events")

        influxdb_config = config.get("influxdb")
        max_workers = config.get("threads", {}).get("max_workers", 10)

        data_processor = DataProcessor(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)
        
        thread = threading.Thread(target=data_processor.run)
        thread.start()
        thread.join()
        # data_processor.run()
    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        if data_processor:
            data_processor.stop()
        print("Closing Kafka consumer==============================")