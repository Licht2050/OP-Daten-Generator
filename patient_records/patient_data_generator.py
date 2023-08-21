

import os
import random

from holiday_record import HolidayPlace
from patient_record import PatientRecordGenerator
from pre_existing_illness import PreExistingIllness
import sys


# sys.path.append('../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../help_classes_and_functions'))
from send_to_kafka import send_to_topic
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender



def generate_patient_data():
    holiday_generator = HolidayPlace()
    patient_generator = PatientRecordGenerator()
    pre_existing_illness_generator = PreExistingIllness()

    patient_record = patient_generator.generate_random_patient_record()

    # Generierung von Urlaubsorten ohne Redundanzen
    num_places = random.randint(1, 5) # Zufällige Anzahl von Urlaubsorten (1 bis 5)
    holiday_places = holiday_generator.generate_random_holiday_places(num_places)


    # Generierung von Vorerkrankungen ohne Redundanzen
    num_illnesses = random.randint(2, 5)
    pre_existing_illnesses = pre_existing_illness_generator.generate_random_pre_existing_illness(num_illnesses)

    return patient_record, holiday_places, pre_existing_illnesses

def send_patient_data(sender, source_name):
    try:
        patient_record, holiday_places, pre_existing_illnesses = generate_patient_data()
        sender.send_single_data(source_name, patient_record)

        for holiday_place in holiday_places:
            sender.send_single_data(source_name, holiday_place)

        for illness_record in pre_existing_illnesses:
            sender.send_single_data(source_name, illness_record)

    except Exception as e:
        print("Error:", e)



if __name__ == "__main__":

    source_name = "patient_records"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    patient_records_config = config_loader.load_config(source_name)

    sender = SourceDataSender(patient_records_config)

    try:
        send_patient_data(sender, source_name)
    except Exception as e:
        print("Error:", e)
    finally:
        sender.disconnect_producer()