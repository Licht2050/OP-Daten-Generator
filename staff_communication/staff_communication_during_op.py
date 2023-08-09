import random
import time
from datetime import datetime
from kafka import KafkaProducer
import json
import sys
sys.path.append('../help_funktions')
from send_to_kafka import send_to_topic
from kafka import KafkaConsumer

class StaffCommunicationGenerator():
    def __init__(self):
        self.doctors = []
        self.nurses = []
        self.anesthetists = []
    
    def load_team_members(self, bootstrap_servers, input_topic):
        consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=bootstrap_servers,
            group_id=None,
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        for message in consumer:
            team_members = message.value
            self.doctors = team_members.get('doctors', [])
            self.nurses = team_members.get('nurses', [])
            self.anesthetists = team_members.get('anesthetists', [])
            break

        consumer.close()


# Generiert realistische Gesprächsnachrichten während der Operation
def generate_operation_conversation():
    sender = random.choice(team_members)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation = [
        "Bitte reichen Sie mir das Skalpell.",
        "Die Blutwerte sehen stabil aus.",
        "Hat jemand die Röntgenbilder?",
        "Die Anästhesie ist gut eingestellt.",
        "Könnten Sie das Licht ein wenig heller machen?",
        "Wir sind gleich fertig, nur noch den letzten Schnitt.",
        "Saugen Sie bitte das Blut ab.",
        "Wir müssen vorsichtig sein, die Arterie ist in der Nähe.",
        "Der Patient hat eine allergische Reaktion, geben Sie Epinephrin.",
        "Wir sind auf gutem Weg, der Eingriff verläuft reibungslos.",
        "Wir benötigen mehr Tupfer.",
        "Kann jemand die Herzfrequenz überwachen?",
        "Gut gemacht, Team!",
        "Die Naht sieht ordentlich aus.",
        "Brauchen wir noch weitere Schmerzmittel?"
    ]
    message = f"[{timestamp}] {sender}: {random.choice(conversation)}"
    return message

def send_conversation(producer, topic, intervall_min=3, intervall_max=20):
    print("OP-Teamgesprächsgenerator gestartet.")
    try:
        while True:
            conversation = generate_operation_conversation()
            send_to_topic(producer, topic, conversation)
            interval_min, interval_max = min(interval_min, interval_max), max(interval_min, interval_max)        
            sleep_time = random.randint(intervall_min, intervall_max)
            time.sleep(sleep_time)# Zufällige Zeitspanne zwischen den Nachrichten
    except KeyboardInterrupt:
        print("Generator stopped.")
    finally:
        producer.flush()

if __name__ == "__main__":
    try:
        bootstrap_server = "192.168.29.120:9092"
        topic = "StaffCommunication"
        intervall_min=3
        intervall_max=20
        producer = KafkaProducer(bootstrap_servers=bootstrap_server)
        send_conversation(producer, topic, intervall_min, intervall_max)
    except Exception as e:
        print("Error: ", e)
    finally:
        producer.close()
    
        
