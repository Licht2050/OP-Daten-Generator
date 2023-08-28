import random
import os
import logging
import sys

# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from config import BLOOD_PRESSURE_SOURCE_NAME, PATIENT_INFO_NAME
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

# Configure logging for the script
logging.basicConfig(level=logging.INFO)


def generate_random_blood_pressure(patient_id):
    """
    Generates a random blood pressure value.
    """
    systolic = random.randint(90, 140)
    diastolic = random.randint(60, 90)
    return {
        "Patient_ID": patient_id,
        "systolic": systolic,
        "diastolic": diastolic
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
        config = config_loader.load_config(BLOOD_PRESSURE_SOURCE_NAME)
        sender = SourceDataSender(config)
        
        # Send continuous data
        sender.send_continuous_data(BLOOD_PRESSURE_SOURCE_NAME, lambda: generate_random_blood_pressure(patient_id))
        
    except Exception as e:
        logging.error(f"Error: {e}")


