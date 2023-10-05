from datetime import datetime
import os
import sys
import threading
import json
from pydantic import ValidationError

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../config'),
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb')),
    os.path.join(os.path.dirname(__file__), '../db_connectors')
])


from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from mongodb_conncetor import MongoDBConnector
from kafka_consumer_wrapper import KafkaConsumerWrapper
from influxdb_connector import InfluxDBConnector
from typing import Dict, Any
from indoor_environment_data_schema import IndoorEnvironmentDataStatus, IndoorEnvironmentDataValue
import traceback
from base import Base

class BaseProcessor(Base):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__()
        self._setup_logging()
        self.patient_entry_exit_events_config = patient_entry_exit_events_config
        self.mongodb_config = mongodb_config
        self.max_workers = max_workers
        self._initialize_kafka_consumer()
        self._initialize_influxdb_connector(influxdb_config)
        self._initialize_mongodb_connector()
        self.current_patients = {}
        self.patients_locks = threading.Lock()


    def _initialize_kafka_consumer(self):
        """Initialize the Kafka consumer."""
        try:
            self.consumer = KafkaConsumerWrapper(
                self.patient_entry_exit_events_config, 
                self._process_patient_entry_exit_events,
                self.max_workers
            )
        except Exception as e:
            self._handle_exception(f"Error starting Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _initialize_mongodb_connector(self):
        self.mongodb_connector = MongoDBConnector(
            host=self.mongodb_config['host'],
            port=self.mongodb_config['port'],
            database_name=self.mongodb_config['database'],
            collection_name=self.mongodb_config['collection']
        )
    
    def _initialize_influxdb_connector(self, influxdb_config: Dict[str, Any] ) -> None:
        """Initialize the InfluxDB connector."""
        try:
            self.influxdb_connector = InfluxDBConnector(**influxdb_config)
        except Exception as e:
            self._handle_exception(f"Error initializing InfluxDB connector: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _process_patient_entry_exit_events(self, message):
        msg = json.loads(message.decode('utf-8'))
        timestamp = msg.get("timestamp")
        value = msg.get("value")
        print(f"Patient entry exit evet-----------------: {value} and time stamp: {timestamp}")
        patient_id = value.get("Patient_ID")

        with self.patients_locks:
            if value.get("event_type") == "patient_entered":
                print(f"Patient entered: {patient_id} and op_room: {value.get('op_room')}")
                op_room = self._fetch_patient_op_room(patient_id)
                self.current_patients[patient_id] = {
                    "op_room": op_room,
                    "timestamp": timestamp
                }
            elif value.get("event_type") == "patient_left":
                del self.current_patients[patient_id]

    def _fetch_patient_op_room(self, patient_id):
        try:
            patient = self.mongodb_connector.find_data({'patient_id': patient_id})
            if patient and 'operation_records' in patient and 'pre_op_record' in patient['operation_records']:
                # print(f"Patinet {patient}")
                return patient['operation_records']['pre_op_record'].get('operation_room')
        except Exception as e:
            self.logger.error(f"Error fetching operation room for patient {patient_id}: {e}")
            return None



    def _convert_to_datetime(self, timestamp_str: str) -> datetime:
        """Convert a timestamp string to datetime."""
        try:
            timestamp_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            return timestamp_obj
        except ValueError:
            self.logger.error(f"Invalid timestamp format: {timestamp_str}")
            return datetime.now()


    def run(self):
        try:
            self.logger.info("Running Kafka consumer==============================")
            self.consumer.consume()
        except Exception as e:
            self._handle_exception(f"Error consuming messages: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def stop(self):  # Neue Methode, um das Herunterfahren zu initiieren
        self.logger.info("====================== Stopping Kafka consumer...")
        self.consumer.close()
        self.mongodb_connector.close()
        self.influxdb_connector.close()

