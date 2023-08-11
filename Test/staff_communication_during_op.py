import random
import time
from datetime import datetime
from kafka import KafkaProducer
import json
import sys
sys.path.append('../help_funktions')
from send_to_kafka import send_to_topic
from kafka import KafkaConsumer
from threading import Lock, Thread

class StaffCommunicationGenerator:
    def __init__(self):
        self.current_people_in_room = []
        # Lock für sichere Aktualisierung
        self.current_people_lock = Lock()  
        self.producer = KafkaProducer(bootstrap_servers="192.168.29.120:9092")
        self.intervall_min = 3
        self.intervall_max = 20
        self.conversation_messages = [
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
    
    def load_team_members(self, input_topic):
        try: 
            consumer = KafkaConsumer(
                input_topic,
                bootstrap_servers="192.168.29.120:9092",
                group_id=None,
                auto_offset_reset='latest',
                enable_auto_commit=False,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )

            for record in consumer:
                message = record.value
                event_type = message["event_type"]
                with self.current_people_lock:
                    if event_type == "Eintritt":
                        self.current_people_in_room.append(message["person"])
                        print(self.current_people_in_room)
                    elif event_type == "Verlassen":
                        if message["person"] in self.current_people_in_room:
                            self.current_people_in_room.remove(message["person"])
                            print(self.current_people_in_room)
        except KeyboardInterrupt:
            print("load stopped.")
        finally:
            consumer.close()

    def generate_operation_conversation(self, sender):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {sender}: {random.choice(self.conversation_messages)}"
        return message

    def send_conversation(self, topic):
        print("OP-Teamgesprächsgenerator gestartet.")
        try:
            while True:
                if len(self.current_people_in_room) >= 2:
                    sender = random.choice(self.current_people_in_room)
                    message_text = random.choice(self.conversation_messages)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    conversation = {
                        "timestamp": timestamp,
                        "sender": sender,
                        "message": message_text
                    }   
                    send_to_topic(self.producer, topic, json.dumps(conversation))
                sleep_time = random.randint(self.intervall_min, self.intervall_max)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("Generator gestoppt.")
        finally:
            self.producer.flush()

if __name__ == "__main__":
    try:
        team_member_topic = "OP_Entry_Exit_Events"
        staff_communication_topic = "Patientenakte"
        
        staff_generator = StaffCommunicationGenerator()
        
        # Starten Sie den Thread für load_team_members
        load_thread = Thread(target=staff_generator.load_team_members, args=(team_member_topic,))
        load_thread.start()
        
        # Führen Sie send_conversation im Hauptthread aus
        staff_generator.send_conversation(staff_communication_topic)
        
        # Warten Sie darauf, dass der Thread load_team_members beendet wird
        load_thread.join()
    except Exception as e:
        print("Fehler: ", e)

