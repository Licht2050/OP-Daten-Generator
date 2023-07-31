

import time
import random
from kafka import KafkaProducer


def generate_random_heart_rate():
    return random.randint(60, 100)

def print_heart_rate(data):
    print(f"Heart Rate: {data} BPM")

def send_random_heart_data(producer, topic, interval_secondes=5):
    try:
        while True:
            heart_rate = generate_random_heart_rate()
            message = f"BPM: {heart_rate}"
            print_heart_rate(heart_rate)
            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval_secondes)
    except KeyboardInterrupt:
        print("Heart Rate Producer stopped")
    finally:
        producer.flush()
        


if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    topic = "Vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    
    try:
        send_random_heart_data(producer, topic)
    except Exception as e:
        print("Error: {e}")

