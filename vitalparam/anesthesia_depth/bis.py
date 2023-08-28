import random
import logging
import sys
import os

# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from config import PATIENT_INFO_NAME, BIS_SOURCE_NAME
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

# Configure logging for the script
logging.basicConfig(level=logging.INFO)

#Narkosetiefe
def generate_random_bis_value(patient_id, min_value, max_value):
    """
    Generates a random bis value between min_value and max_value.

    Args:
        min_value (int): The minimum bis value.
        max_value (int): The maximum bis value.

    Returns:
        float: A random bis value.
    """
    bis_value = round(random.uniform(min_value, max_value), 2)
    return {
        "Patient_ID": patient_id,
        "bis_value": bis_value
    }



if __name__ == "__main__":
    patient_info_path = os.path.join(os.path.dirname(__file__), '../../consume_patient_details/patient_info.json')
    patient_info_config_loader = ConfigLoader(patient_info_path)
    patient_details = patient_info_config_loader.load_config(PATIENT_INFO_NAME)
    patient_id = patient_details["Patient_ID"]

    
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    try:
        # Load configurations and initialize sender
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(BIS_SOURCE_NAME)
        sender = SourceDataSender(config)
        
        # Send continuous data
        sender.send_continuous_data(BIS_SOURCE_NAME, lambda: generate_random_bis_value(patient_id, 50, 60))
    except Exception as e:
        logging.error(f"Error: {e}")