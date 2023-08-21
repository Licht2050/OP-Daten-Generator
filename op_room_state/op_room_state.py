import os
import sys
import time
import random
from kafka import KafkaProducer
# sys.path.append('../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../help_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender



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
    


if __name__ == "__main__":

    source_name = "op_room_state"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    op_room_state_config = config_loader.load_config(source_name)

    sender = SourceDataSender(op_room_state_config)
    generator = OPRoomStateGenerator()
    print("OP-Raumstatus-Generator gestartet.") 

    try:
        sender.send_continuous_data(source_name, lambda: generator.generate_op_room_status())
    except Exception as e:
        print("Error: {e}")
    finally:
        sender.disconnect_producer()