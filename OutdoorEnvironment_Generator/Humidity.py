import time
import random
from kafka import KafkaProducer


#Generierung einer zufälligen Luftfeuchtigkeit im Bereich von 30% bis 70%
def generate_random_humidity():
    return round(random.uniform(30.0, 70.0), 2)

def send_humidity(producer, topic, interval=5):
    print("Luftfeuchtigkeitsgenerator gestartet:")
    try:
        while True:
            humidity = generate_random_humidity()
            message = f"Luftfeuchtigkeit: {humidity}%"
            producer.send(topic, value=message.encode('utf-8'))
            print(message)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Generator gestoppt.")
    finally:
        producer.flush()


if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    topic = "Environmentalinfo"

    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    try:
        send_humidity(producer, topic)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.close()
