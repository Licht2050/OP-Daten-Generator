

import logging
import random
import os
import sys
# sys.path.append('../../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../help_classes_and_functions'))
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

#Atemwegsüberwachung
def generate_random_etco2_value(min_value, max_value):
    return random.randint(min_value, max_value)


if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    sensor_name = "etco2"
    try:
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        sender.send_continuous_data(sensor_name, lambda: generate_random_etco2_value(30, 50))
    except Exception as e:
        logging.error(f"Error: {e}")