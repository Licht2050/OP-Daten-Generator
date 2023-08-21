

import os
import sys
import random
import logging
# sys.path.append('../../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../help_classes_and_functions'))
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

def generate_random_oxygen_saturation(min_value=90, max_value=100):
    return random.randint(min_value, max_value)


if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    sensor_name = "oxygen_saturation"
    try:
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        sender.send_continuous_data(sensor_name, lambda: generate_random_oxygen_saturation(90, 100))
    except Exception as e:
        logging.error(f"Error: {e}")