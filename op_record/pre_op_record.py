import json
import logging
import os
import random
from datetime import datetime, timedelta
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

logging.basicConfig(level=logging.INFO)

class PreOperationRecordGenerator:

    def __init__(self, config_loader, patient_config_loader):
        operation_details = config_loader.load_config("operation_details")
        patient_details = patient_config_loader.load_config("patient_details")
        if operation_details is None or patient_details is None:
            raise ValueError("Config file could not be loaded.")
        
        self.patient_id = patient_details["Patient_ID"]
        self.operation_rooms = operation_details["operation_rooms"]
        self.operation_types = operation_details["operation_types"]
        self.operation_duration_range = tuple(operation_details["operation_duration_range"])
        self.operation_date_offset_range = tuple(operation_details["operation_date_offset_range"])
        self.anaesthesia_types = operation_details["anaesthesia_types"]
        self.medical_devices = operation_details["medical_devices"]
        self.medications = operation_details["medications"]
    

    def generate_operation_date(self):
        now = datetime.now()
        operation_date = now + timedelta(seconds=random.randint(*self.operation_date_offset_range))
        return operation_date.strftime("%d.%m.%Y %H:%M:%S")

    def generate_operation_duration(self):
        return f"{random.randint(*self.operation_duration_range)} minutes"

    def generate_pre_operation_record(self):
        pre_operation_record = {
            "Patient_ID": self.patient_id,
            "Operation_Type": random.choice(self.operation_types),
            "Operation_Room": random.choice(self.operation_rooms),
            "Duration": self.generate_operation_duration(),
            "Date": self.generate_operation_date(),
            "Anaesthesia_Type": random.choice(self.anaesthesia_types),
            "Medical_Devices": random.sample(self.medical_devices, 2),
            "Medications": random.sample(self.medications, 2)
        }

        return pre_operation_record
    
if __name__ == "__main__":
    source_name = 'op_record'
    op_config_file_path = os.path.join(os.path.dirname(__file__), '../config/op_config.json')
    op_config_loader = ConfigLoader(op_config_file_path)
    patient_info_path = os.path.join(os.path.dirname(__file__), '../consume_patient_details/patient_info.json')
    patient_config_loader = ConfigLoader(patient_info_path)

    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    sender_config_loader = ConfigLoader(config_file_path)
    sender_config = sender_config_loader.load_config(source_name)

    
    pre_op_generator = PreOperationRecordGenerator(op_config_loader, patient_config_loader)
    sender = SourceDataSender(sender_config)
    try: 
        pre_op_record = pre_op_generator.generate_pre_operation_record() 
        sender.send_single_data("pre_op_record", pre_op_record)
    except Exception as e:
        logging.error(f"Error: {e}")