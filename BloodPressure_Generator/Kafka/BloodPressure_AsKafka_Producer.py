import random
import time
from kafka import KafkaProducer

def generate_random_blood_pressure():
    systolic = random.randint(90, 140)
    diastolic = random.randint(60, 90)
    return systolic, diastolic

def display_blood_pressure(systolic, diastolic):
    print(f"Systolic: {systolic} mmHg, Diastolic: {diastolic} mmHg")


def send_blood_pressure_data(producer, topic, interval_seconds=5):
    try:
        while True:
            systolic, diastolic = generate_random_blood_pressure()
            message = f"Systolic: {systolic}, Diastolic: {diastolic}"
            producer.send(topic, value=message.encode('utf-8'))
            display_blood_pressure(systolic, diastolic)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Data streaming stopped.")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":

    bootstrap_server = "localhost:9092"
    topic = "Vitalparameter"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    try:
        send_blood_pressure_data(producer, topic)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()

