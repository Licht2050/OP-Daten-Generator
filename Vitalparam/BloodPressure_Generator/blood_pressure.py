import random
import time
from datetime import datetime

# Generiert Blutdruck-Messwerte
def generate_blood_pressure():
    systolic = random.randint(90, 180)
    diastolic = random.randint(60, 120)
    return systolic, diastolic

# Prüft auf kritische Blutdruckwerte und löst ggf. einen Notfallalarm aus
def check_blood_pressure(systolic, diastolic):
    if systolic > 160 or diastolic > 100:
        return True
    return False

# Generiert Notfallalarm-Meldungen
def generate_emergency_alarm(emergency_type, location):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] DRINGEND: {emergency_type} in {location}! Sofortige medizinische Hilfe erforderlich."
    return message

if __name__ == "__main__":
    while True:
        systolic, diastolic = generate_blood_pressure()
        if check_blood_pressure(systolic, diastolic):
            emergency_type = "Kritischer Blutdruck"
            location = "OP-Saal"
            message = generate_emergency_alarm(emergency_type, location)
            print(message)
        time.sleep(random.randint(5, 20))  # Zufällige Zeitspanne zwischen den Messungen
