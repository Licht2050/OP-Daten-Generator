

import time
import random
from kafka import KafkaProducer

#Atemwegsüberwachung
def generate_random_etco2_value():
    return random.randint(12, 20)

def print_respiratory(data):
    print(f"Respiratory rate: {data} breaths per minute.")

def send_respiratory_etco2_value(producer, topic, interval_seconds=5):
    try:
        while True:
            respiratory_rate = generate_random_etco2_value()
            print_respiratory(respiratory_rate)
            message = f"EtCO2: {respiratory_rate}"
            
            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Respiratory streaming stopped.")
    finally:
        producer.flush()

if __name__ == "__main__":

    bootstrap_server = "localhost:9092"
    topic = "Vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        send_respiratory_etco2_value(producer, topic)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()