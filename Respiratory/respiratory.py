

import time
import random
from kafka import KafkaProducer

#Atemwegsüberwachung
def generate_random_respiratory_rate():
    return random.randint(12, 20)

def print_respiratory(data):
    print(f"Respiratory rate: {data} breaths per minute.")

def send_respiratory_monitoring_data(producer, topic, interval_seconds=5):
    try:
        while True:
            respiratory_rate = generate_random_respiratory_rate()
            print_respiratory(respiratory_rate)
            data = str(respiratory_rate)
            
            producer.send(topic, value=data.encode())
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Respiratory streaming stopped.")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":

    bootstrap_server = "localhost:9092"
    topic = "Vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    send_respiratory_monitoring_data(producer, topic)