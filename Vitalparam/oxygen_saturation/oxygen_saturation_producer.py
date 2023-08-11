

import time
import random
from kafka import KafkaProducer


def generate_random_oxygen_saturation():
    return random.randint(90, 100)

def print_oxygen_saturation(data):
    print(f"Oxygen Saturation: {data}%")

def send_oxygen_saturation_data(producer, topic, interval_seconds=5):
    try:
        while True:
            oxygen_saturation = generate_random_oxygen_saturation()
            print_oxygen_saturation(oxygen_saturation)
            message = f"Oxygen Saturation: {oxygen_saturation}"
            
            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Oxygen saturation streaming stopped.")
    finally:
        producer.flush()

if __name__ == "__main__":

    bootstrap_server = "192.168.29.120:9093"
    topic = "vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        send_oxygen_saturation_data(producer, topic)
    except Exception as e:
        print("Error: {e}")
    finally:
        producer.close()