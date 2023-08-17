

import logging
import os
import random
import sys
sys.path.append('../../help_classes_and_functions')
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader


def generate_random_heart_rate(min_value, max_value):
    return random.randint(min_value, max_value)
        

if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    sensor_name = "heart_rate"
    try:
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        sender.send_continuous_data(sensor_name, lambda: generate_random_heart_rate(60, 100))
    except Exception as e:
        logging.error(f"Error: {e}")