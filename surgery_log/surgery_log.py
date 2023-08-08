import random
import time
from datetime import datetime

team_members = ["Dr. Schmidt", "Dr. Müller", "Schwester Anna", "Anästhesist Alex", "Chirurgin Sarah"]

# Generiert Nachrichten für OP-Vorbereitungen
def generate_operation_preparation():
    sender = random.choice(team_members)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {sender}: Vorbereitungen für die nächste Operation treffen."
    return message

# Generiert Nachrichten für Notfälle im OP
def generate_emergency():
    sender = random.choice(team_members)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] DRINGEND: {sender} - Notfall im OP! Sofortige Aufmerksamkeit erforderlich."
    return message

# Generiert Nachrichten für OP-Planänderungen
def generate_schedule_change():
    sender = random.choice(team_members)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {sender}: Änderung im OP-Plan - Bitte überprüfen."
    return message

if __name__ == "__main__":
    generatoren = [generate_operation_preparation, generate_emergency, generate_schedule_change]
    
    while True:
        generator = random.choice(generatoren)
        message = generator()
        print(message)
        time.sleep(random.randint(10, 60))  # Zufällige Zeitspanne zwischen den Nachrichten
