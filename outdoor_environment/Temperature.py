import random
import time

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

 