

import os
import sys
import time
import random
# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import SECONDS_IN_YEAR


class PreExistingIllness:
    """
    Represents a generator for pre-existing illnesses.

    Attributes:
        illnesses (list): List of potential illnesses.
        treatments (list): List of potential treatments.
        diagnosed_range (tuple): Range for randomizing the diagnosed date.
        treated_range (tuple): Range for randomizing the treated date.
    """
    def __init__(self, illnesses, treatments, diagnosed_range, treated_range):
        self.illnesses = illnesses
        self.treatments = treatments
        # Zeitraum für Diagnosedatum: 3 bis 15 Jahre zurück
        self.diagnosed_range = diagnosed_range
        # Zeitraum für Behandlungsdatum: 1 bis 6 Jahre nach Diagnose
        self.treated_range = treated_range

    def _generate_random_date(self, start_date, date_range):
        """
        Generate a random date based on the given range.

        Args:
            start_date (int): The starting date as a timestamp.
            date_range (tuple): Range for randomizing the date.
        
        Returns:
            str: The generated random date.
        """
        start_time = start_date - date_range[1]
        end_time = start_date - date_range[0]
        random_timestamp = random.randint(start_time, end_time)
        return time.strftime("%d.%m.%Y", time.localtime(random_timestamp))

 
    def generate_random_diagnose_date(self):
        """
        Generate a random diagnosed date.

        Returns:
            str: The generated random diagnosed date.
        """
        now = int(time.time())
        return self._generate_random_date(now, self.diagnosed_range)
    
    def generate_random_treated_date(self, diagnosed_date):
        """
        Generate a random treated date based on the diagnosed date.

        Args:
            diagnosed_date (str): The diagnosed date.
        
        Returns:
            str: The generated random treated date.
        """
        diagnosed_timestamp = int(time.mktime(time.strptime(diagnosed_date, "%d.%m.%Y")))
        return self._generate_random_date(
            diagnosed_timestamp, 
            (-self.treated_range[1], -self.treated_range[0])
        )

 
    def generate_random_pre_existing_illness(self, num_illnesses, patient_ids):
        """
        Generate random pre-existing illness records.

        Args:
            num_illnesses (int): Number of illness records to generate.
        
        Returns:
            list: List of dictionaries containing illness records.
        """
        selected_illnesses = random.sample(self.illnesses, min(len(self.illnesses), num_illnesses))

        illness_records = []
        for illness in selected_illnesses:
            diagnosed_date = self.generate_random_diagnose_date()
            treatment = random.choice(self.treatments)
            treated_date = self.generate_random_treated_date(diagnosed_date)

            illness_record = {
                "Patient_ID": patient_ids,
                "Vorerkrankung": illness,
                "Diagnosedatum": diagnosed_date,
                "Behandlung": treatment,
                "Behandlungsdatum": treated_date,
                "Weitere Informationen": "..."
            }
            illness_records.append(illness_record)

        return illness_records

