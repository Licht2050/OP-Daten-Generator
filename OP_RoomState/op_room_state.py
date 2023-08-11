import time
import random
from kafka import KafkaProducer

class OPRoomStateGenerator:
    def __init__(self):
        self.door_states = ["Offen", "Geschlossen"]
    
    def generate_op_room_status(self):
        door_state = random.choice(self.door_states)
        temprature = round(random.uniform(20.0, 25.0), 2)
        humidity = round(random.uniform(30.0, 60.0), 2)
        pressure = round(random.uniform(980.0, 1020.0), 2)
        illumination = round(random.uniform(200.0, 1000.0), 2)

        op_room_status = {
            "Türzustand": door_state,
            "Raumtemperatur": temprature,
            "Luftfeuchtigkeit": humidity,
            "Luftdruck": pressure,
            "Bleuchtungsstärke": illumination
        }

        return op_room_status
    
def send_op_room_status(producer, topic, interval=10):
    generator = OPRoomStateGenerator()
    print("OP-Raumstatus-Generator gestartet.") 
    try:
        while True:
            op_room_status = generator.generate_op_room_status()
            print(op_room_status)
            message = f"{op_room_status}"
            producer.send(topic, value=message.encode('utf-8'))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Generator gestoppt.")
    finally:
        producer.flush()


if __name__ == "__main__":
    bootstrap_server = "192.168.29.120:9094"
    topic = "op_raum_status"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    try:
        send_op_room_status(producer, topic)
    except Exception as e:
        print("Error: {e}")
    finally:
        producer.close()