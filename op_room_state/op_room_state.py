import logging
import os
import sys
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender


# Konstanten
TEMP_RANGE = (20.0, 25.0)
HUMIDITY_RANGE = (30.0, 60.0)
PRESSURE_RANGE = (980.0, 1020.0)
ILLUMINATION_RANGE = (200.0, 1000.0)
DOOR_STATES = ["Offen", "Geschlossen"]


class OPRoomStateGenerator:
    """Klasse zur Generierung des OP-Raum-Status."""
    def __init__(self, config_file_path, source_name, op_record_path, op_details_name):
        self.source_name = source_name
        self.op_details_name = op_details_name

        self._setup_logging()
        self._load_configuration(config_file_path, op_record_path)
        self._setup_sender()
        
    def _setup_logging(self):
        """Initializes the logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _load_configuration(self, config_file_path, op_record_path):
        """Loads the required configurations."""
        config_loader = ConfigLoader(config_file_path)
        self.room_state_config = config_loader.load_config(SOURCE_NAME)

        op_record_config_loader = ConfigLoader(op_record_path)
        self.op_record_config = op_record_config_loader.load_config(OP_DETAILS_NAME)

    def _setup_sender(self):
        """Initializes the sender for data."""
        self.sender = SourceDataSender(self.room_state_config)

    def generate_op_room_status(self):
        """Generate a random OP room status."""
        door_state = random.choice(DOOR_STATES)
        temprature = round(random.uniform(*TEMP_RANGE), 2)
        humidity = round(random.uniform(*HUMIDITY_RANGE), 2)
        pressure = round(random.uniform(*PRESSURE_RANGE), 2)
        illumination = round(random.uniform(*ILLUMINATION_RANGE), 2)

        op_room_status = {
            "Operation_Room": self.op_record_config["Operation_Room"],
            "Türzustand": door_state,
            "Raumtemperatur": temprature,
            "Luftfeuchtigkeit": humidity,
            "Luftdruck": pressure,
            "Bleuchtungsstärke": illumination
        }

        return op_room_status
    
    def start(self):
        """Start the OP room state generator."""
        self.logger.info("OP-Raumstatus-Generator gestartet.")
        try:
            self.sender.send_continuous_data(self.source_name, lambda: self.generate_op_room_status())
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            self.sender.disconnect_producer()

if __name__ == "__main__":
    OP_DETAILS_NAME = 'op_details'
    SOURCE_NAME = "op_room_state"
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')

    OP_RECORD_PATH = os.path.join(os.path.dirname(__file__), '../consume_op_record/op_record.json')

    
    generator = OPRoomStateGenerator(CONFIG_FILE_PATH, SOURCE_NAME, OP_RECORD_PATH, OP_DETAILS_NAME)
    generator.start()
