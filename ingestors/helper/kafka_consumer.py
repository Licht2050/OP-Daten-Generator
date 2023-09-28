import asyncio
import os
import sys
from kafka import KafkaConsumer
import json
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from base import Base

class KafkaTopicConsumer(Base):
    """A class for consuming messages from a Kafka topic."""

    def __init__(self, config, callback=None, max_workers=10):
        """
        Initialize Kafka consumer.

        Args:
            config (dict): Configuration settings.
            callback (function, optional): Function to process consumed messages. Defaults to None.
            max_workers (int, optional): Maximum number of worker threads. Defaults to 10.
        """
        super().__init__()
        self._setup_logging()

        self.bootstrap_servers = config.get('bootstrap_servers')
        self.topic_name = config.get('topic_name')
        self.group_id = config.get('group_id')
        self.auto_offset_reset = config.get('auto_offset_reset', 'latest')

        self.callback = callback
        self.executor = ThreadPoolExecutor(max_workers)

        value_deserializer = config.get('value_deserializer', lambda x: json.loads(x.decode('utf-8')))

        self.consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            value_deserializer=value_deserializer
        )


    def close(self):
        """Close Kafka consumer connection."""
        self.consumer.close()

    def consume(self):
        """Consume messages from Kafka topic."""
        self.consumer.subscribe([self.topic_name])

        # neue integration:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            for message in self.consumer:
                if self.callback:
                    # neue integration:
                    if asyncio.iscoroutinefunction(self.callback):
                        future = loop.run_until_complete(self.callback(message.value))
                    else:
                        # alte integration:
                        self.executor.submit(self.callback, message.value)
                else:
                    self.logger.info(f"Received message: {message.value}")
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user. Closing connections...")
            self.close()  # Closing the Kafka consumer connection
            self.logger.info("Connections closed. Exiting.")
        except Exception as e:
            self._handle_exception(f"Error while consuming data: {e}")
        finally:
            self.close()
            loop.close()




def process_message(message):
    print(f"Processing message: {message}")

if __name__ == "__main__":
    config = {
        'bootstrap_servers': 'localhost:9092',
        'topic_name': 'staff_communication',
        'group_id': 'staff_communication_to_influxdb',
        'auto_offset_reset': 'earliest'
    }

    consumer = KafkaTopicConsumer(config, callback=process_message)
    consumer.consume()
