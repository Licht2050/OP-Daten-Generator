import time
import random
from kafka import KafkaProducer

class OutdoorEnvironmentGenerator:
    
    def generate_outdoor_environment_info(self):
        temperature = round(random.uniform(-10.0, 40.0), 2)
        humidity = round(random.uniform(30.0, 80.0), 2)
        pressure = round(random.uniform(980.0, 1050.0), 2)
        wind_speed = round(random.uniform(0.0, 30.0), 2)

        outdoor_environment = {
            "Außentemperatur": temperature,
            "Luftfeuchtigkeit": humidity,
            "Luftdruck": pressure,
            "Windgeschwindigkeit": wind_speed,
        }

        return outdoor_environment
    
def send_outdoor_environment_info(producer, topic, interval=10):
    generator = OutdoorEnvironmentGenerator()
    print("Umweltparameter-Generator für draußen gestartet:") 
    try:
        while True:
            outdoor_environment = generator.generate_outdoor_environment_info()
            print(outdoor_environment)
            message = f"{outdoor_environment}"
            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Generator gestoppt.")
    finally:
        producer.flush()


if __name__ == "__main__":
    bootstrap_server = "192.168.29.120:9092"
    topic = "umgebungsdaten"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    try:
        send_outdoor_environment_info(producer, topic)
    except Exception as e:
        print("Error: {e}")
    finally:
        producer.close()