import asyncio
import datetime
import sys
import os
from threading import Lock
import threading
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
from middelware_manager_async import MiddlewareManager
from process_entry_exit_events import DataProcessor
from graphql_publisher import GraphQLPublisher


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
        return self.middleware_manager.process_middlewares(message)

    
    async def _process_and_save_message(self, data) -> None:
        """Process and save the message."""
        try:
            processed_message = await self.process_middleware(data)
            # print(f"Processed message------------------: {processed_message}")
            schema = self.create_operation_room_status_schema(processed_message.to_dict()) 
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
        
        value_data_dict = value_data.model_dump()
        fields = {key: value for key, value in value_data_dict.items() if key != "op_room"}

        schema = {
            "measurement": source,
            "tags": {
                "op_room": value_data.op_room,
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
    handler = None
    data_processor = None
    thread = None
    loop = asyncio.get_event_loop()
    try:
        config_loader = ConfigLoader(CONFIG_FILE_PATH)
        config = config_loader.get_all_configs()
        entry_exit_events_config = config.get("topics", {}).get("entry_exit_events")
        influxdb_config = config.get("influxdb")
        max_workers = config.get("threads", {}).get("max_workers", 10)

        mongodb_config = config.get("op_details")
        patient_entry_exit_events_config = config.get("topics", {}).get("patient_entry_exit_events")

        pub_sub_config = config.get("publish_subscribe_channels")
        subscribe_channel = pub_sub_config.get("entry_exit_events").get("subscribe_channel")

        """Add a suffix to the group_id to make it unique"""
        patient_entry_exit_events_config['group_id'] = patient_entry_exit_events_config['group_id'] + "_entry_exit_events"


        graphql_publisher = GraphQLPublisher(subscribe_channel)


        data_processor = DataProcessor(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)
        thread = threading.Thread(target=data_processor.run)
        thread.start()

        loop.run_until_complete(graphql_publisher.initialize())

        handler = EntryExisEventHandler(entry_exit_events_config, influxdb_config, max_workers=max_workers)
        handler.add_middleware(data_processor.process_data)
        handler.add_middleware(graphql_publisher.process_data)
        handler.run()

        thread.join()
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
            loop.run_until_complete(graphql_publisher.close_redis())
        threading.join(timeout=5) # Wait for the thread to finish
        if thread.is_alive():
            print("Thread hat nicht rechtzeitig geantwortet und wird erzwungen beendet.")
