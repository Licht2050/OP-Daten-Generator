

import logging
import random
import os
import sys


# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from config import ETCO2_RANGE, ETCO2_SOURCE_NAME, PATIENT_INFO_NAME
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

# Configure logging for the script
logging.basicConfig(level=logging.INFO)

#Atemwegsüberwachung
def generate_random_etco2_value(patient_id, min_value, max_value):
    """
    Generates a random etco2 value between min_value and max_value.

    Args:
        min_value (int): The minimum etco2 value.
        max_value (int): The maximum etco2 value.

    Returns:
        float: A random etco2 value.
    """
    etco2_value = random.randint(min_value, max_value)
    return {
        "Patient_ID": patient_id,
        "etco2": etco2_value
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
        config = config_loader.load_config(ETCO2_SOURCE_NAME)
        sender = SourceDataSender(config)

        # Send continuous data
        sender.send_continuous_data(ETCO2_SOURCE_NAME, lambda: generate_random_etco2_value(patient_id, *ETCO2_RANGE))
    except Exception as e:
        logging.error(f"Error: {e}")