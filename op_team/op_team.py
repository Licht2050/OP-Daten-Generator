import random
import json

import sys
sys.path.append('../help_funktions')
from send_to_kafka import send_to_topic
from kafka import KafkaProducer


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
    op_team_generator = OPTeamGenerator()
    bootstrap_server = "localhost:9092"
    topic = "OPTeam"
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_server)
        op_team = op_team_generator.generate_op_team()
        send_to_topic(producer, topic, op_team)
        
        print()
    except Exception as e:
        print("Error: ", e)
    finally:
        producer.close()