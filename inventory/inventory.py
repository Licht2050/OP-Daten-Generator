import random
import time
from datetime import datetime

inventory_items = ["Verbandsmaterial", "Chirurgische Instrumente", "Medikamente", "Handschuhe", "Desinfektionsmittel"]

# Generiert Meldungen für Bestandsänderungen
def generate_inventory_change():
    item = random.choice(inventory_items)
    change_type = random.choice(["hinzugefügt", "entfernt", "aktualisiert"])
    quantity = random.randint(1, 100)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Bestandsänderung: {change_type} {quantity} Einheiten von {item}."
    return message

# Generiert Meldungen für kritischen Bestand
def generate_low_inventory_alert():
    item = random.choice(inventory_items)
    threshold = random.randint(1, 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] DRINGEND: Kritischer Bestand erreicht! Nur noch {threshold} Einheiten von {item} verfügbar."
    return message

# Generiert Meldungen für neue Lieferung
def generate_delivery_notification():
    item = random.choice(inventory_items)
    delivery_provider = random.choice(["Lieferant A", "Lieferant B", "Lieferant C"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] Neue Lieferung erhalten: {item} von {delivery_provider}."
    return message

if __name__ == "__main__":
    generators = [generate_inventory_change, generate_low_inventory_alert, generate_delivery_notification]
    
    while True:
        generator = random.choice(generators)
        message = generator()
        print(message)
        time.sleep(random.randint(30, 120))  # Zufällige Zeitspanne zwischen den Meldungen
