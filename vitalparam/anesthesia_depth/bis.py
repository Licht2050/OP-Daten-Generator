import random
import logging
import sys
import os

# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))

from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

# Configure logging for the script
logging.basicConfig(level=logging.INFO)

#Narkosetiefe
def generate_random_bis_value(min_value, max_value):
    """
    Generates a random bis value between min_value and max_value.

    Args:
        min_value (int): The minimum bis value.
        max_value (int): The maximum bis value.

    Returns:
        float: A random bis value.
    """
    return round(random.uniform(min_value, max_value), 2)


if __name__ == "__main__":
    sensor_name = "bis"
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    try:
        # Load configurations and initialize sender
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        
        # Send continuous data
        sender.send_continuous_data(sensor_name, lambda: generate_random_bis_value(50, 60))
    except Exception as e:
        logging.error(f"Error: {e}")