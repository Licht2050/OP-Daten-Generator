

import logging
import os
import random
import sys



# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))

# Configure logging for the script
logging.basicConfig(level=logging.INFO)


from source_data_sender import SourceDataSender
from config_loader import ConfigLoader


def generate_random_heart_rate(min_value, max_value):
    """
    Generates a random heart rate value between min_value and max_value.
    
    Args:
        min_value (int): The minimum heart rate value.
        max_value (int): The maximum heart rate value.

    Returns:
        float: A random heart rate value.
    """
    return random.randint(min_value, max_value)
        

if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    sensor_name = "heart_rate"

    try:
        # Load configurations and initialize sender
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)

        # Send continuous data
        sender.send_continuous_data(sensor_name, lambda: generate_random_heart_rate(60, 100))
    except Exception as e:
        logging.error(f"Error: {e}")