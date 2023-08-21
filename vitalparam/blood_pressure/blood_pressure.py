import random
import os
import logging
import sys


# Den Pfad zum Hauptordner hinzufügen
# sys.path.append('../../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../help_classes_and_functions'))

from source_data_sender import SourceDataSender
from config_loader import ConfigLoader
logging.basicConfig(level=logging.INFO)

def generate_random_blood_pressure():
    systolic = random.randint(90, 140)
    diastolic = random.randint(60, 90)
    return {
        "Systolic": systolic,
        "Diastolic": diastolic
    }



if __name__ == "__main__":
    # Pfade zur Konfigurationsdatei suchen
    config_file_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
    sensor_name = "blood_pressure"
    try:
        config_loader = ConfigLoader(config_file_path)
        config = config_loader.load_config(sensor_name)
        sender = SourceDataSender(config)
        
        sender.send_continuous_data(sensor_name, generate_random_blood_pressure)
        
    except Exception as e:
        logging.error(f"Error: {e}")

