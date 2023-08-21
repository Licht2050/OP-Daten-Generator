from datetime import datetime
import sys
import time
import json
from kafka import KafkaProducer
import logging
from config_loader import ConfigLoadError
# sys.path.append('../../config')


logging.basicConfig(level=logging.INFO)



class SourceDataSender:
    def __init__(self, config):
        self.config = config
        self.producer = None
        
    def connect_producer(self):
        if self.producer is None:
            if self.config is None:
                raise ConfigLoadError("Config not loaded")
            bootstrap_server = self.config["bootstrap_servers"]
            self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    
    def disconnect_producer(self):
        if self.producer is not None:
            self.producer.close()
            self.producer = None
        
    def generate_source_message(self, source_name, data):
        message = {
            "source": source_name,
            "value": data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return json.dumps(message)
    
    def send_single_data(self, source_name, data):
        try:
            self.connect_producer()
            topic = self.config["topic"]
            
            source_value = data
            message = self.generate_source_message(source_name, source_value)
            logging.info(f"{source_name} single message: {message}")
            if self.producer is not None:
                self.producer.send(topic, message.encode("utf-8"))
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            if self.producer is not None:
                self.producer.flush()

    def send_continuous_data(self, source_name, generate_function):
        try:
            self.connect_producer()
            topic = self.config["topic"]
            interval_seconds = self.config["interval_seconds"]
            while True:
                source_value = generate_function()
                message = self.generate_source_message(source_name, source_value)
                logging.info(f"{source_name} message: {message}")
                if self.producer is not None:
                    self.producer.send(topic, message.encode("utf-8")) 
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logging.info(f"{source_name} streaming stopped.")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            self.disconnect_producer()
