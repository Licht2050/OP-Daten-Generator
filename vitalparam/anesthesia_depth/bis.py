import random
import logging
import sys
import os

# Den Pfad zum Hauptordner hinzufügen
# sys.path.append('../../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../help_classes_and_functions'))

from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

logging.basicConfig(level=logging.INFO)

#Narkosetiefe
def generate_random_bis_value(min_value, max_value):
    return round(random.uniform(min_value, max_value), 2)


if __name__ == "__main__":
    sensor_name = "bis"
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    try:
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        
        sender.send_continuous_data(sensor_name, lambda: generate_random_bis_value(50, 60))
    except Exception as e:
        logging.error(f"Error: {e}")