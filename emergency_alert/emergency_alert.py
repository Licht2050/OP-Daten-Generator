import random
import time
from datetime import datetime

emergency_types = ["Herzstillstand", "Atemnot", "Schwerer Blutverlust", "Bewusstlosigkeit", "Kritischer Blutdruck"]

# Generiert Notfallalarm-Meldungen
def generate_emergency_alarm():
    emergency_type = random.choice(emergency_types)
    location = random.choice(["OP-Saal", "Intensivstation", "Notaufnahme", "Patientenzimmer"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] DRINGEND: {emergency_type} in {location}! Sofortige medizinische Hilfe erforderlich."
    return message

if __name__ == "__main__":
    while True:
        message = generate_emergency_alarm()
        print(message)
        time.sleep(random.randint(5, 20))  # Zufällige Zeitspanne zwischen den Meldungen
