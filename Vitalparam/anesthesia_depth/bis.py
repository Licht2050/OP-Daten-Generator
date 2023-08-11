import random
import time
from kafka import KafkaProducer

#Narkosetiefe
def generate_random_bis_value():
    return round(random.uniform(50, 60), 2)

def print_anesthesia_depth(data):
    print(f"Bispectral Index (BIS) value: {data}")

def send_bis_data(producer, topic, interval_seconds=5):
    try:
        while True:
            anesthesia_depth = generate_random_bis_value()
            print_anesthesia_depth(anesthesia_depth)
            message = f"BIS-Value: {anesthesia_depth}"

            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("BIS streaming stopped.")
    finally:
        producer.flush()
        


if __name__ == "__main__":

    bootstrap_server = "192.168.29.120:9092"
    topic = "vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    try:
        send_bis_data(producer, topic)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()