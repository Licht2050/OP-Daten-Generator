import datetime
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
    os.path.join(os.path.dirname(__file__), '../db_connectors')
])


from influxdb_connector import InfluxDBConnector
from base import Base
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager import MiddlewareManager
from process_entry_exit_events import DataProcessor


class EntryExisEventHandler(Base):
    
    def __init__(self, entry_exit_events_config: Dict[str, Any] , influxdb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()
        self._setup_logging()
        self.entry_exit_events_config = entry_exit_events_config
        self.influxdb_config = influxdb_config
        self.max_workers = max_workers
        self.middleware_manager = MiddlewareManager()
        self.lock = Lock()
        self._initialize_influxdb_connector(influxdb_config)
        self._start_consumer()

    def _initialize_influxdb_connector(self, influxdb_config: Dict[str, Any] ) -> None:
        """Initialize the InfluxDB connector."""
        try:
            self.influxdb_connector = InfluxDBConnector(**influxdb_config)
        except Exception as e:
            self._handle_exception(f"Error initializing InfluxDB connector: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _start_consumer(self) -> None:
        """Initialize and start the Kafka consumer."""
        try:
            self.consumer = KafkaTopicConsumer(
                config=self.entry_exit_events_config,
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

    
    def _process_and_save_message(self, data) -> None:
        """Process and save the message."""
        try:
            processed_message = self.process_middleware(data)
            # print(f"Processed message------------------: {processed_message}")
            schema = self.create_operation_room_status_schema(processed_message) 
            self.influxdb_connector.write_points([schema])
        except Exception as e:
            self._handle_exception(f"Error processing message: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def create_operation_room_status_schema(self, processed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a schema for the operation_room_status measurement."""
        timestamp_str = processed_message.get("timestamp")
        timestamp = self._convert_timestamp(timestamp_str) if timestamp_str else self._get_current_timestamp()
        
        value_data = processed_message.get("value", {})
        source = processed_message.get("source")

        fields = {key: value for key, value in value_data.items() if key != "Operation_Room"}

        schema = {
            "measurement": source,
            "tags": {
                "Operation_Room": value_data.get("Operation_Room"),
            },
            "time": timestamp,
            "fields": fields
        }
        return schema

    def _get_current_timestamp(self) -> str:
        """Get the current timestamp in ISO format."""
        return datetime.datetime.utcnow().isoformat() + "Z"
    
    def _convert_timestamp(self, timestamp_str: str) -> str:
        """Convert a timestamp string to ISO format."""
        try:
            timestamp_obj = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            return timestamp_obj.isoformat() + "Z"
        except ValueError:
            self.logger.error(f"Invalid timestamp format: {timestamp_str}")
            return self._get_current_timestamp()
        
    def run(self):
        """Start the Kafka consumer."""
        try:
            self.consumer.consume()
        except Exception as e:
            self._handle_exception(f"Error running Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            self.consumer.close()
            self.lock.release()

if __name__ == "__main__":

    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs()
    entry_exit_events_config = config.get("topics", {}).get("entry_exit_events")
    influxdb_config = config.get("influxdb")
    max_workers = config.get("threads", {}).get("max_workers", 10)

    data_processor = DataProcessor()

    handler = EntryExisEventHandler(entry_exit_events_config, influxdb_config, max_workers=max_workers)
    handler.add_middleware(data_processor.process_data)
    handler.run()