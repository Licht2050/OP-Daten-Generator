
import json
from kafka import KafkaProducer

def send_to_topic(producer, topic, message):
    
    try:
        msg = json.dumps(message)
        print(message)
        producer.send(topic, value=str(msg).encode('utf-8'))
    except Exception as e:
        print("Error: ", e)
    finally:
        producer.flush()