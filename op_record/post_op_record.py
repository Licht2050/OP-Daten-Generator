import logging
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

logging.basicConfig(level=logging.INFO)

class PostOperationRecordGenerator:

    def __init__(self, config_loader, patient_config_loader):
        operation_details = config_loader.load_config("operation_details")
        patient_details = patient_config_loader.load_config("patient_details")
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
    source_name = 'op_record'
    op_config_file_path = os.path.join(os.path.dirname(__file__), '../config/op_config.json')
    op_config_loader = ConfigLoader(op_config_file_path)
    patient_info_path = os.path.join(os.path.dirname(__file__), '../consume_patient_details/patient_info.json')
    patient_config_loader = ConfigLoader(patient_info_path)

    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    sender_config_loader = ConfigLoader(config_file_path)
    sender_config = sender_config_loader.load_config(source_name)

    

    post_op_generator = PostOperationRecordGenerator(op_config_loader, patient_config_loader)
    sender = SourceDataSender(sender_config)
    try: 
        pre_op_record = post_op_generator.generate_post_operation_record() 
        sender.send_single_data("post_op_record", pre_op_record)
    except Exception as e:
        logging.error(f"Error: {e}")