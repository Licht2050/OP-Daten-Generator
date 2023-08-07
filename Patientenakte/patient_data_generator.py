import json
import random
from holiday_record import HolidayPlace
from patient_record import PatientRecordGenerator
from pre_existing_illness import PreExistingIllness

def generate_patient_data():
    holiday_generator = HolidayPlace()
    patient_generator = PatientRecordGenerator()
    pre_existing_illness_generator = PreExistingIllness()

    patient_record = patient_generator.generate_random_patient_record()

    # Generierung von Urlaubsorten ohne Redundanzen
    num_places = random.randint(1, 5) # Zufällige Anzahl von Urlaubsorten (1 bis 5)
    holiday_places = holiday_generator.generate_random_holiday_places(num_places)


    # Generierung von Vorerkrankungen ohne Redundanzen
    num_illnesses = random.randint(0, 5)
    pre_existing_illnesses = pre_existing_illness_generator.generate_random_pre_existing_illness(num_illnesses)

    return patient_record, holiday_places, pre_existing_illnesses

def send_patient_data(producer, topic):
    try:
        patient_record, holiday_places, pre_existing_illnesses = generate_patient_data()
        message = json.dumps(patient_record)
        producer.send(topic, value=str(message).encode('utf-8'))
        print(patient_record)

        for holiday_place in holiday_places:
            message = json.dumps(holiday_place)
            producer.send(topic, value=str(message).encode('utf-8'))
            print(holiday_place)

        for illness_record in pre_existing_illnesses:
            message = json.dumps(illness_record)
            producer.send(topic, value=str(message).encode('utf-8'))
            print(illness_record)

    except Exception as e:
        print("Error:", e)
    finally:
        producer.flush()