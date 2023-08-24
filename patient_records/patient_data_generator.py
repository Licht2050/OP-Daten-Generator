

import logging
import os
import random

from holiday_record import HolidayPlace
from patient_record import PatientRecordGenerator
from pre_existing_illness import PreExistingIllness
import sys


# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

# Set up basic logging for the script
logging.basicConfig(level=logging.INFO)

TOPIC_NAMES = {
    "patient_records": "patient_records",
    "holiday_records": "holiday_records",
    "illness_records": "illness_records"
}

def generate_patient_data():
    """
    Generates a comprehensive patient record including personal data,
    holiday destinations, and pre-existing illnesses.
    
    Returns:
        tuple: A tuple containing patient record, holiday places, and pre-existing illnesses
    """
    holiday_generator = HolidayPlace()
    patient_generator = PatientRecordGenerator()
    pre_existing_illness_generator = PreExistingIllness()

    patient_record = patient_generator.generate_random_patient_record()
    patient_id = patient_record["Patient_ID"]

    # Generate a list of unique holiday destinations
    num_places = random.randint(1, 5) # Random number of holiday places (1 to 5)
    holiday_places = holiday_generator.generate_random_holiday_places(num_places, patient_id)


    # Generate a list of unique pre-existing illnesses
    num_illnesses = random.randint(2, 5)
    pre_existing_illnesses = pre_existing_illness_generator.generate_random_pre_existing_illness(num_illnesses, patient_id)

    return patient_record, holiday_places, pre_existing_illnesses

def send_patient_data(sender, source_name):
    """
    Sends the generated patient data, holiday places, and pre-existing illnesses 
    to the specified destination.
    
    Args:
        sender (SourceDataSender): An instance responsible for sending data.
        source_name (str): The name of the topic where data is sent.
    """
    patient_record = None
    try:
        patient_record, holiday_places, pre_existing_illnesses = generate_patient_data()

        # Send the main patient record
        sender.send_single_data(TOPIC_NAMES["patient_records"], patient_record)

        # Send each holiday destination
        for holiday_place in holiday_places:
            sender.send_single_data(TOPIC_NAMES["holiday_records"], holiday_place)

        # Send each pre-existing illness record
        for illness_record in pre_existing_illnesses:
            sender.send_single_data(TOPIC_NAMES["illness_records"], illness_record)

    except Exception as e:
        logging.error(f"Error during data sending: {e}")
        if patient_record:
            logging.error("Patient Record: %s", patient_record)



if __name__ == "__main__":

    source_name = "patient_records"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    patient_records_config = config_loader.load_config(source_name)

    sender = SourceDataSender(patient_records_config)

    try:
        send_patient_data(sender, source_name)
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
    finally:
        sender.disconnect_producer()