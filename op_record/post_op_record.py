import os
import random
from datetime import datetime, timedelta
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader


class PostOperationRecordGenerator:

    def __init__(self, config_loader, patient_config_loader):
        operation_details = config_loader.load_config("operation_details")
        self.operation_outcomes = operation_details["operation_outcomes"]

    def generate_post_operation_record(self):
        post_operation_record = {
            "Operation_Outcome": random.choice(self.operation_outcomes),
            "Notes": "Keine besonderen Vorfälle während der Operation."
        }

        return post_operation_record

if __name__ == "__main__":
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/op_config.json')
    config_loader = ConfigLoader(config_file_path)
    patient_info_path = os.path.join(os.path.dirname(__file__), 'patient_info.json')

    post_op_generator = PostOperationRecordGenerator(config_loader, patient_info_path)
    print(post_op_generator.generate_post_operation_record())
