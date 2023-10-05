import logging
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH, PATIENT_INFO_NAME, PATIENT_INFO_PATH, PATIENT_ENTRY_EXIT_EVENTS_SOURCE_NAME
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader


# Set up logging
logging.basicConfig(level=logging.INFO)


def generate_patient_exit_event(patient_info_config):

    patient_entry_exit_events = {
        "Patient_ID": patient_info_config["Patient_ID"],
        "event_type": "patient_left"
    }
    return patient_entry_exit_events



def main():
    
        
    patient_info_config_loader = ConfigLoader(PATIENT_INFO_PATH)
    patient_info_config = patient_info_config_loader.load_config(PATIENT_INFO_NAME)


    
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    op_team_config = config_loader.load_config(PATIENT_ENTRY_EXIT_EVENTS_SOURCE_NAME)

    sender = SourceDataSender(op_team_config)
    

    try:
        patient_entry_exit_events = generate_patient_exit_event(patient_info_config)
        sender.send_single_data(PATIENT_ENTRY_EXIT_EVENTS_SOURCE_NAME, patient_entry_exit_events)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sender.disconnect_producer()

    
if __name__ == "__main__":
    main()
    