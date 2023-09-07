import os
import sys
from kafka import KafkaConsumer
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from base import Base

class KafkaTopicConsumer(Base):
    """A class for consuming messages from a Kafka topic."""

    def __init__(self, config, callback=None):
        """
        Initialize Kafka consumer.

        Args:
            config (dict): Configuration settings.
            callback (function, optional): Function to process consumed messages. Defaults to None.
        """
        super().__init__()
        self._setup_logging()

        self.bootstrap_servers = config.get('bootstrap_servers')
        self.topic_name = config.get('topic_name')
        self.group_id = config.get('group_id')
        self.auto_offset_reset = config.get('auto_offset_reset', 'latest')

        self.callback = callback

        value_deserializer = config.get('value_deserializer', lambda x: json.loads(x.decode('utf-8')))

        self.consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            value_deserializer=value_deserializer
        )


    def consume(self):
        """Consume messages from Kafka topic."""
        self.consumer.subscribe([self.topic_name])

        try:
            for message in self.consumer:
                if self.callback:
                    self.callback(message.value)
                else:
                    self.logger.info(f"Received message: {message.value}")

        except Exception as e:
            self._handle_exception(f"Error while consuming data: {e}")



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
