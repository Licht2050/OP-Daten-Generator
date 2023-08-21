import os
import random
import sys
# sys.path.append('../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../help_classes_and_functions'))
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader


class OPTeamGenerator:
    def __init__(self):

        self.doctors = [
            "Dr. Müller", "Dr. Schmidt", "Dr. Schneider", "Dr. Fischer", "Dr. Weber",
            "Dr. Wagner", "Dr. Becker", "Dr. Hoffmann", "Dr. Schäfer", "Dr. Koch"
        ]

        self.nurses = [
            "Krankenschwester Müller", "Krankenschwester Schmidt", "Krankenschwester Schneider",
            "Krankenschwester Fischer", "Krankenschwester Weber", "Krankenschwester Wagner",
            "Krankenschwester Becker", "Krankenschwester Hoffmann", "Krankenschwester Schäfer",
            "Krankenschwester Koch"
        ]

        self.anesthetists = [
            "Anästhesist Müller", "Anästhesist Schmidt", "Anästhesist Schneider",
            "Anästhesist Fischer", "Anästhesist Weber", "Anästhesist Wagner",
            "Anästhesist Becker", "Anästhesist Hoffmann", "Anästhesist Schäfer",
            "Anästhesist Koch"
        ]

    def generate_op_team(self):
        team_size = random.randint(2, 3)  # Zufällige Größe des Teams (3 bis 6)
        team = {
            "doctors": random.sample(self.doctors, team_size),
            "nurses": random.sample(self.nurses, team_size),
            "anesthetists": random.sample(self.anesthetists, team_size)
        }
        return team




    
if __name__ == "__main__":

    source_name = "op_team"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    op_team_config = config_loader.load_config(source_name)

    sender = SourceDataSender(op_team_config)
    op_team_generator = OPTeamGenerator()

    try:
        op_team = op_team_generator.generate_op_team()
        sender.send_single_data(source_name, op_team)
    except Exception as e:
        print("Error: ", e)
    finally:
        sender.disconnect_producer()