import logging
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH, OP_CONFIG_FILE_PATH, OP_RECORD_SOURCE_NAME, OPERATION_DETAILS_NAME, PATIENT_INFO_NAME, PATIENT_INFO_PATH, POST_RECORD_SOURCE_NAME
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

logging.basicConfig(level=logging.INFO)

class PostOperationRecordGenerator:

    def __init__(self, config_loader, patient_config_loader):
        operation_details = config_loader.load_config(OPERATION_DETAILS_NAME)
        patient_details = patient_config_loader.load_config(PATIENT_INFO_NAME)
        if operation_details is None or patient_details is None:
            raise ValueError("Config file could not be loaded.")
        
        self.patient_id = patient_details["Patient_ID"]
        self.operation_outcomes = operation_details["operation_outcomes"]

    def generate_post_operation_record(self):
        post_operation_record = {
            "Patient_ID": self.patient_id,
            "Operation_Outcome": random.choice(self.operation_outcomes),
            "Notes": "Keine besonderen Vorfälle während der Operation."
        }

        return post_operation_record

if __name__ == "__main__":
    
    op_config_loader = ConfigLoader(OP_CONFIG_FILE_PATH)
    patient_config_loader = ConfigLoader(PATIENT_INFO_PATH)

    sender_config_loader = ConfigLoader(CONFIG_FILE_PATH)
    sender_config = sender_config_loader.load_config(OP_RECORD_SOURCE_NAME)

    

    post_op_generator = PostOperationRecordGenerator(op_config_loader, patient_config_loader)
    sender = SourceDataSender(sender_config)
    try: 
        pre_op_record = post_op_generator.generate_post_operation_record() 
        sender.send_single_data(POST_RECORD_SOURCE_NAME, pre_op_record)
    except Exception as e:
        logging.error(f"Error: {e}")