from kafka import KafkaConsumer
import json

class GeneralKafkaConsumer:
    """
    A general Kafka consumer that reads messages from a given topic.
    """
    def __init__(self, topic, bootstrap_servers, auto_offset_reset='latest'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=auto_offset_reset,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def consume_messages(self):
        """
        Yield messages from Kafka.
        """
        for message in self.consumer:
            yield message
    
    def close(self):
        """
        Close the consumer connection.
        """
        self.consumer.close()
