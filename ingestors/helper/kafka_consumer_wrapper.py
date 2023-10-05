import json
import os
import sys
import threading
from confluent_kafka import Consumer, KafkaError
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from base import Base

class KafkaConsumerWrapper(Base):
    def __init__(self, config, callback, max_workers=10):
        self.config = config
        self.callback = callback
        self.executer = ThreadPoolExecutor(max_workers)
        self._stop_event = threading.Event()
        self.value_deserializer = lambda x: json.loads(x.decode('utf-8'))
        self._initialize_consumer()


    def _initialize_consumer(self):
        conf = {
            'bootstrap.servers': self.config['bootstrap_servers'],
            'group.id': self.config['group_id'],
            'auto.offset.reset': 'latest'
        }

        self.consumer = Consumer(conf)
        self.consumer.subscribe([self.config.get('topic_name')])

    

    def consume(self):
        try:
            while not self._stop_event.is_set():
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(f"Reached end of topic {msg.topic()} partition {msg.partition()} at offset {msg.offset()}")
                    else:
                        self.logger.info(f"Error while consuming message: {msg.error()}")
                else:
                    # value = self.value_deserializer(msg.value())
                    if self.callback:
                        # self.callback(value)
                        
                        self.executer.submit(self.callback, msg.value())
                    else:
                        value = self.value_deserializer(msg.value())
                        self.logger.info('Received message: {}'.format(value))
        except Exception as e:
            self.logger.error(f"Error consuming messages: {e}")
            raise

    def close(self):
        """Close Kafka consumer connection."""
        self._stop_event.set()
        self.consumer.close()
    
