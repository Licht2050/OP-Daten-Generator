

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
            data = str(oxygen_saturation)
            
            producer.send(topic, value=data.encode())
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Oxygen saturation streaming stopped.")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":

    bootstrap_server = "localhost:9092"
    topic = "Vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    send_oxygen_saturation_data(producer, topic)