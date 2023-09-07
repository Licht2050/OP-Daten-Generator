from datetime import datetime
import sys
import time
import json
from kafka import KafkaProducer
import logging
from config_loader import ConfigLoadError
# sys.path.append('../../config')


logging.basicConfig(level=logging.INFO)


class KafkaConnectionError(Exception):
    """Raised when there's an issue connecting to Kafka."""
    pass

class KafkaSendMessageError(Exception):
    """Raised when there's an error sending a message to Kafka."""
    pass


class SourceDataSender:
    def __init__(self, config):
        if config is None:
            raise ConfigLoadError("Config not provided")
        
        self.config = config
        self.producer = None
        
    def connect_producer(self):
        """Establishes a connection with Kafka producer."""
        if self.producer is None:
            try:
                bootstrap_server = self.config["bootstrap_servers"]
                self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
            except Exception as e:
                raise KafkaConnectionError(f"Error connecting to Kafka: {e}")
    
    def disconnect_producer(self):
        """Closes the connection with Kafka producer."""
        if self.producer is not None:
            self.producer.close()
            self.producer = None
    
    def ensure_connected(self):
        """Ensures that producer is connected."""
        if self.producer is None:
            self.connect_producer()
            if self.producer is None:
                raise KafkaConnectionError("Producer not connected")

    def generate_source_message(self, source_name, data):
        """Generates the source message."""
        message = {
            "source": source_name,
            "value": data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        return json.dumps(message)
    
    def send_message(self, message):
        """Sends a message to Kafka."""
        try:
            if self.producer is None:
                raise KafkaConnectionError("Producer not connected")
            self.producer.send(self.config["topic"], message.encode("utf-8"))
            self.producer.flush()
        except Exception as e:
            raise KafkaSendMessageError(f"Error sending message to Kafka: {e}")

    def send_single_data(self, source_name, data):
        """Sends single data to Kafka."""
        self.ensure_connected()
        message = self.generate_source_message(source_name, data)
        logging.info(f"{source_name} single message: {message}")
        self.send_message(message)

    def send_continuous_data(self, source_name, generate_function):
        """Sends data continuously to Kafka."""
        self.ensure_connected()
        interval_seconds = self.config["interval_seconds"]
        try:    
            while True:
                source_value = generate_function()
                message = self.generate_source_message(source_name, source_value)
                logging.info(f"{source_name} message: {message}")
                self.send_message(message)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logging.info(f"{source_name} streaming stopped.")
            self.disconnect_producer()
        except Exception as e:
            raise KafkaSendMessageError(f"Error sending continuous data to Kafka: {e}")
        finally:
            self.disconnect_producer()
