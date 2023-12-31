import logging
import os
import sys
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import (CONFIG_FILE_PATH, OP_DETAILS_NAME, OP_RECORD_PATH, 
                    DOOR_STATES, OP_ROOM_STATE_SOURCE_NAME, TEMP_RANGE, 
                    HUMIDITY_RANGE, PRESSURE_RANGE, ILLUMINATION_RANGE,
                    CO2_RANGE, NOISE_RANGE, UV_INDEX_RANGE
                    )
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender



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
        self.room_state_config = config_loader.load_config(OP_ROOM_STATE_SOURCE_NAME)

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
        illuminance  = round(random.uniform(*ILLUMINATION_RANGE), 2)
        co2_level = round(random.uniform(*CO2_RANGE), 2)
        noise_level = round(random.uniform(*NOISE_RANGE), 2) 
        uv_index = round(random.uniform(*UV_INDEX_RANGE), 2)

        

        op_room_status = {
            "Operation_Room": self.op_record_config["Operation_Room"],
            "Türzustand": door_state,
            "Raumtemperatur": temprature,
            "Luftfeuchtigkeit": humidity,
            "Luftdruck": pressure,
            "Beleuchtungsstärke": illuminance,
            "CO2_Level": co2_level,
            "Lärmpegel": noise_level,
            "UV-Index": uv_index
        }

        return op_room_status
    
    def start(self):
        """Start the OP room state generator."""
        self.logger.info("Indoor_Environment_Data-Generator gestartet.")
        try:
            self.sender.send_continuous_data(self.source_name, lambda: self.generate_op_room_status())
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            self.sender.disconnect_producer()

if __name__ == "__main__":
    

    
    generator = OPRoomStateGenerator(CONFIG_FILE_PATH, OP_ROOM_STATE_SOURCE_NAME, OP_RECORD_PATH, OP_DETAILS_NAME)
    generator.start()
