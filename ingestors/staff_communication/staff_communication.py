
import asyncio
import os
import sys
import threading
import traceback
from typing import Any, Dict
import logging



sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))

from base import Base
from paths_config import CONFIG_FILE_PATH
from datetime import datetime
from config_loader import ConfigLoader
from process_staff_communication import DataProcessor
from kafka_consumer import KafkaTopicConsumer
from influxdb_connector import InfluxDBConnector
from concurrent.futures import ThreadPoolExecutor
from middelware_manager_async import MiddlewareManager
from graphql_publisher import GraphQLPublisher


class StaffCommunicationHandler(Base):
    def __init__(self, staffC_config: Dict[str, Any], influxdb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()
        self._setup_logging()
        self.max_workers = max_workers
        self.influxdb_connector = InfluxDBConnector(**influxdb_config)
        self.executor = ThreadPoolExecutor(self.max_workers)
        self.middleware_manager = MiddlewareManager()

        self._start_consumer(staffC_config)


    def _start_consumer(self, staff_config) -> None:
        """Initialize and start the Kafka consumer."""
        try:
            self.consumer = KafkaTopicConsumer(
                config=staff_config,
                callback=self.process_and_save_data,
                max_workers=self.max_workers
            )
            
        except Exception as e:
            self._handle_exception(f"Error starting Kafka consumer: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def add_middleware(self, middleware_fn):
        self.middleware_manager.add_middleware(middleware_fn)
    
    def process_middleware(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process the message through the middleware manager."""
        return self.middleware_manager.process_middlewares(message)

    async def process_and_save_data(self, data: Dict[str, Any]) -> None:
        try:
            
            # Step 1: Process data through middlewares
            processed_message = await self.process_middleware(data)

            # print(f"processed_message: {processed_message.raw_message}")

            # Step 2: Write the processed data to InfluxDB
            shema = self.create_staff_communication_schema(processed_message.raw_message) 
            self.influxdb_connector.write_points([shema])
            # print(f"shema: {shema}")
        except Exception as e:
            self._handle_exception(f"Error while processing and saving data: {e}")


    def create_staff_communication_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a schema for the staff_communication measurement.

        Args:
            data (dict): The staff communication data.

        Returns:
            dict: The InfluxDB schema.
        """
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            timestamp_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            timestamp_iso = timestamp_obj.isoformat() + "Z"
        else:
            raise ValueError("Timestamp not found in data")
        
        value_data = data.get("value", {})
        schema = {
            "measurement": "staff_communication",
            "tags": {
                "Operation_Room": value_data.get("op_room", "Unknown"),
                "sender": value_data.get("sender", "Unknown"),
            },
            "time": timestamp_iso,
            "fields": {
                "message": value_data.get("message", ""),
            }
        }
        return schema

    def run(self) -> None:
        # Start consuming messages from Kafka
        self.consumer.consume()
    
    def stop(self):
        self.consumer.shutdown()
        self.executor.shutdown(wait=False)
        self.influxdb_connector.close()
        self.logger.info("Staff communication handler stopped.")



if __name__ == "__main__":
    handler = None
    data_processor = None
    handler = None
    thread = None
    loop = asyncio.get_event_loop()
    try:
        # Load the configuration
        config_loader = ConfigLoader(CONFIG_FILE_PATH)
        config = config_loader.get_all_configs()

        staffC_config = config.get("topics", {}).get("staff_communication")
        influxdb_config = config.get("influxdb")
        mongodb_config = config.get("op_details")
        max_workers = config.get("threads", {}).get("max_workers", 10)
        patient_entry_exit_events_config = config.get("topics", {}).get("patient_entry_exit_events")

        """Add a suffix to the group_id to make it unique"""
        patient_entry_exit_events_config['group_id'] = patient_entry_exit_events_config['group_id'] + "_staff_communication"

        # Instantiate the data processor and the staff communication handler
        data_processor = DataProcessor(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)
        thread = threading.Thread(target=data_processor.run)
        thread.start()


        pub_sub_config = config.get("publish_subscribe_channels")
        subscribe_channel = pub_sub_config.get("staff_communication").get("subscribe_channel")
        graphql_publisher = GraphQLPublisher(subscribe_channel)
        loop.run_until_complete(graphql_publisher.initialize())


        handler = StaffCommunicationHandler(staffC_config, influxdb_config, max_workers=max_workers)

        # Add the data processor as a middleware
        handler.add_middleware(data_processor.process_data)
        handler.add_middleware(graphql_publisher.process_data)
        # Run the handler to start the process

        handler.run()
        thread.join()
    except KeyboardInterrupt:
        logging.info("Stopping the staff communication handler...")
    finally:
        if data_processor is not None:
            data_processor.stop()
        if handler is not None:
            handler.stop()
        if graphql_publisher is not None:
            loop.run_until_complete(graphql_publisher.close_redis())
        thread.join(timeout=5) # Wait for the thread to finish
        if thread.is_alive():
            print("Thread hat nicht rechtzeitig geantwortet und wird erzwungen beendet.")
    