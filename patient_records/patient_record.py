

import logging
import random
import sys
import time
import csv
import os
import uuid
# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import SECONDS_IN_YEAR

# Set up basic logging for the script
logging.basicConfig(level=logging.INFO)

class PatientRecordGenerator:
    """
    Generates random patient records with unique patient IDs, names, gender, addresses, etc.
    Manages patient IDs through a CSV file to ensure uniqueness across different runs.
    """

    
    CSV_FILENAME = 'patient_ids.csv'
    def __init__(self, names, name_by_gender, genders, streets, cities, postal_codes, blood_groups, weight_range, height_range):
        self.patient_ids = set()
        self.names = names
        self.name_by_gender = name_by_gender
        self.genders = genders
        self.streets = streets
        self.cities = cities
        self.postal_codes = postal_codes
        self.blood_groups = blood_groups
        self.weight_range = weight_range
        self.height_range = height_range
        # Load existing patient IDs
        self.patient_ids_filename = os.path.join(os.path.dirname(__file__), self.CSV_FILENAME)
        self.patient_ids = self.load_existing_ids()
        

    def load_existing_ids(self):
        """
        Loads existing patient IDs from a CSV file.

        Returns:
            set: A set of existing patient IDs.
        """
        try:
            with open(self.patient_ids_filename, 'r') as file:
                reader = csv.reader(file)
                existing_ids = set(row[0] for row in reader)
            return existing_ids
        except FileNotFoundError:
            return set()
        
    def save_new_id(self, patient_id):
        """
        Saves a new patient ID to the CSV file.

        Args:
            patient_id (str): The patient ID to be saved.
        """
        mode = 'a' if os.path.exists(self.patient_ids_filename) else 'w'
        try:
            with open(self.patient_ids_filename, mode) as file:
                writer = csv.writer(file)
                writer.writerow([patient_id])
        except Exception as e:
            logging.error(f"Error during saving patient ID: {e}")   


    def generate_random_birth_date(self):
        """
        Generates a random birth date within the last ten years.

        Returns:
            str: A birth date in the format "dd.mm.yyyy".
        """
        now = int(time.time())
        #Geburtsdatum in den letzten drei Jahren
        ten_years_ago = now - (SECONDS_IN_YEAR * 10)
        return time.strftime("%d.%m.%Y", time.localtime(random.randint(ten_years_ago, now)))

    def generate_random_patient_id(self):
        """
        Generates a unique UUID as patient ID.

        Returns:
            str: A unique patient ID as UUID.
        """
        patient_id = str(uuid.uuid4())
        if patient_id not in self.patient_ids:
            self.save_new_id(patient_id)
            self.patient_ids.add(patient_id)
            return patient_id

    def generate_random_patient_record(self): 
        """
        Generates a random patient record.

        Returns:
            dict: A dictionary containing patient details.
        """
        patient_id = self.generate_random_patient_id()
        gender = random.choice(self.genders)
        first_name = random.choice(self.name_by_gender[gender])

        last_name = random.choice(self.names)

        

        patient_record = {
            "Patient_ID": patient_id,
            "Name": last_name,
            "Vorname": first_name,
            "Geschlecht": gender,
            "Geburtsdatum": self.generate_random_birth_date(),
            "Straße": random.choice(self.streets),
            "Stadt": random.choice(self.cities),
            "Postleitzahl": random.choice(self.postal_codes),
            "Blutgruppe": random.choice(self.blood_groups),
            "Gewicht": random.randint(*self.weight_range),
            "Größe": random.randint(*self.height_range) 
        }

        return patient_record
    


