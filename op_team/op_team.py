import logging
import os
import random
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH, OP_TEAM_SOURCE_NAME, PATIENT_INFO_NAME, PATIENT_INFO_PATH
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader


# Set up logging
logging.basicConfig(level=logging.INFO)

class OPTeamGenerator:
    """
    This class is responsible for generating a random operation team consisting of doctors, 
    nurses, and anesthetists.
    """
    def __init__(self, patient_info_config):
        """Initializes lists of doctors, nurses, and anesthetists."""
        self.patient_info_config = patient_info_config
        self.doctors = self._initialize_names("Dr.")
        self.nurses = self._initialize_names("Krankenschwester")
        self.anesthetists = self._initialize_names("Anästhesist")

    def _initialize_names(self, prefix):
        """
        Helper method to generate names for medical professionals.

        Args:
            prefix (str): The prefix to add before the last name (e.g., "Dr.")

        Returns:
            list: A list of names with the given prefix.
        """
        last_names = [
            "Müller", "Schmidt", "Schneider", "Fischer", "Weber",
            "Wagner", "Becker", "Hoffmann", "Schäfer", "Koch"
        ]
        return [f"{prefix} {name}" for name in last_names]

    def generate_op_team(self):
        """
        Generates a random operation team.

        Returns:
            dict: A dictionary containing lists of doctors, nurses, and anesthetists.
        """
        team_size = random.randint(2, 3)  # Zufällige Größe des Teams (2 bis 3)
        team = {
            "Patient_ID": self.patient_info_config["Patient_ID"],
            "doctors": random.sample(self.doctors, team_size),
            "nurses": random.sample(self.nurses, team_size),
            "anesthetists": random.sample(self.anesthetists, team_size)
        }
        return team



def main():
    """
    Main execution function.
    Loads the configuration, initializes the sender and generator, and sends a random operation team.
    """
        
    patient_info_config_loader = ConfigLoader(PATIENT_INFO_PATH)
    patient_info_config = patient_info_config_loader.load_config(PATIENT_INFO_NAME)


    
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    op_team_config = config_loader.load_config(OP_TEAM_SOURCE_NAME)

    sender = SourceDataSender(op_team_config)
    op_team_generator = OPTeamGenerator(patient_info_config)

    try:
        op_team = op_team_generator.generate_op_team()
        sender.send_single_data(OP_TEAM_SOURCE_NAME, op_team)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sender.disconnect_producer()

    
if __name__ == "__main__":
    main()
    