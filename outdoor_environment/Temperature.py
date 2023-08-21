import random
import time
from kafka import KafkaProducer

#Generierung einer zufälligen Temperatur im Bereich von 20°C bis 40°C
def generate_random_temperature():
    return round(random.uniform(20.0, 40.0), 2)

def send_temperature(producer, topic, interval=5):
    print("Temperaturgenerator gestartet:")
    try:
        while True:
            temperature = generate_random_temperature()
            message = f"Temperature: {temperature}°C"
            producer.send(topic, value=message.encode('utf-8'))
            print(message)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Temperaturgenerator gestoppt.")
    finally:
        producer.flush()


if __name__ == "__main__":

    bootstrap_server = "localhost:9092"
    topic = "Environmentalinfo"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        send_temperature(producer, topic)
    except Exception as e:
        print("Error: {e}")
    finally:
        producer.close()        