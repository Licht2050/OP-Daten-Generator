import asyncio
import datetime
import sys
import os
from threading import Lock
import threading
import traceback
from typing import Any, Dict

from pydantic import BaseModel
import signal




sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../config'),
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../helper'),
    os.path.join(os.path.dirname(__file__), '../db_connectors'),
    os.path.join(os.path.dirname(__file__), '../data_publisher'),
])

from data_publisher_singleton import DataPublisherSingleton
from influxdb_connector import InfluxDBConnector
from base import Base
from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from middelware_manager_async import MiddlewareManager
from process_indoor_environment_data import DataProcessor
from graphql_publisher import GraphQLPublisher
from mongodb_conncetor import MongoDBConnector


class IndoorEnvironmentDataHandler(Base):
    
    def __init__(self, indoor_environment_config: Dict[str, Any], patient_etnry_exit_events_config: Dict[str, Any] , influxdb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()  # Initialize logger

        self.indoor_environment_config = indoor_environment_config
        self.patient_entry_exit_events_config = patient_etnry_exit_events_config
        self.influxdb_config = influxdb_config
        self.max_workers = max_workers
        self.middleware_manager = MiddlewareManager()
        self.lock = Lock()
        self.influxdb_config = influxdb_config
        self.current_patient_id = []

        self.influxdb_connector = None
        self.consumer = None


    def initialize(self):
        """Initialize all necessary components."""
        self._setup_logging()
        self._initialize_influxdb_connector()
        self._start_consumer()

    def _initialize_influxdb_connector(self) -> None:
        """Initialize the InfluxDB connector."""
        try:
            self.influxdb_connector = InfluxDBConnector(**self.influxdb_config)
        except Exception as e:
            self._log_and_raise_exception(f"Error initializing InfluxDB connector: {e}")
    
    def _start_consumer(self) -> None:
        """Initialize and start the Kafka consumer."""
        try:
            self.consumer = KafkaTopicConsumer(
                config=self.indoor_environment_config,
                callback=self._process_and_save_message,
                max_workers=self.max_workers
            )
            
        except Exception as e:
            self._log_and_raise_exception(f"Error starting Kafka consumer: {e}")
    
    def _log_and_raise_exception(self, message: str) -> None:
        """Log the error and raise the exception."""
        self.logger.error(message)
        self.logger.error(traceback.format_exc())
        raise Exception(message)

    def add_middleware(self, middleware: Any) -> None:
        """Add a middleware to the middleware manager."""
        self.middleware_manager.add_middleware(middleware)
    
    def process_middleware(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process the message through the middleware manager."""
        return self.middleware_manager.process_middlewares(message)

    
    async def _process_and_save_message(self, data) -> None:
        """Process and save the message."""
        try:
            # print(f"Processed message------------------: {data}")
            processed_message = await self.process_middleware(data)
            
            schema = self.create_operation_room_status_schema(processed_message.to_dict()) 
            self.influxdb_connector.write_points([schema])
        except Exception as e:
            self._log_and_raise_exception(f"Error processing message: {e}")

    def create_operation_room_status_schema(self, processed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a schema for the operation_room_status measurement."""
        print(f"Processed message------------------: {processed_message}")
        timestamp_str = processed_message.get("timestamp")
        
        timestamp = self._convert_timestamp(timestamp_str) if timestamp_str else self._get_current_timestamp()
        

        value_data = processed_message.get("value", {})
        tag_field = value_data
        indoor_environment_value = value_data.model_dump(by_alias=False)

        source = processed_message.get("source", "indoor_environment_data")

        fields = {key: value for key, value in indoor_environment_value.items() if key != "op_room"}

        schema = {
            "measurement": source,
            "tags": {
                "op_room": indoor_environment_value.get("op_room"),
            },
            "time": timestamp,
            "fields": fields
        }
        return schema

    @staticmethod
    def _get_current_timestamp() -> str:
        """Get the current timestamp in ISO format."""
        return datetime.datetime.utcnow().isoformat() + "Z"


    def _convert_timestamp(self, timestamp_str: str) -> str:
        """Convert a timestamp string to ISO format."""
        print(f"timestamp_str------------------: {timestamp_str}")
        try:
            timestamp_obj = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            return timestamp_obj.isoformat() + "Z"
        except ValueError:
            self.logger.error(f"Invalid timestamp format: {timestamp_str}")
            return self._get_current_timestamp()
    
    def stop(self):
        self.logger.info("Stopping data_processor...")
        if self.consumer:
            self.consumer.close()
        self.logger.info("data_processor stopped.")

    def run(self):
        """Start the Kafka consumer."""
        try:
            self.initialize()
            self.consumer.consume()
        except Exception as e:
            self._handle_exception(f"Error running Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self.stop()





if __name__ == "__main__":
    graphql_publisher = None
    data_processor = None
    handler = None
    thread = None
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

        graphql_publisher = GraphQLPublisher()

        asyncio.run(graphql_publisher.initialize())
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(graphql_publisher.initialize())
        
        handler = IndoorEnvironmentDataHandler(indoor_environment_config, patient_entry_exit_events_config , influxdb_config, max_workers=max_workers)

        handler.add_middleware(data_processor.process_data)
        handler.add_middleware(graphql_publisher.process_data)
        handler.run()
    except KeyboardInterrupt:
        print("Interrupted by user. Closing connections...")
    except Exception as e:
        print(f"Error starting IndoorEnvironmentDataHandler: {e}")
        print(traceback.format_exc())
    finally:
        print(f"finally is called")
        if data_processor is not None:
            data_processor.stop()
        if handler is not None:
            handler.stop()
        if graphql_publisher is not None:
            asyncio.run(graphql_publisher.close_redis())
            # loop.run_until_complete(graphql_publisher.close_redis())
        thread.join(timeout=5) # Wait for the thread to finish
        if thread.is_alive():
            print("Thread hat nicht rechtzeitig geantwortet und wird erzwungen beendet.")
    