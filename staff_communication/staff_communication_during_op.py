import logging
import os
import random
import time
import json
import sys
from kafka import KafkaConsumer
from threading import Lock, Thread
sys.path.append('../help_classes_and_functions')
from source_data_sender import SourceDataSender
from config_loader import ConfigLoadError, ConfigLoader


class StaffCommunicationGenerator:
    def __init__(self, entry_exit_events_config , staff_communication_config, sender):
        self.entry_exit_events_config = entry_exit_events_config
        self.staff_communication_config = staff_communication_config
        self.sender = sender
        self.consumer = None
        self.current_people_in_room = []
        # Lock für sichere Aktualisierung
        self.current_people_lock = Lock()  
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

    def connect_consumer(self):
        if self.consumer is None:
            if not self.entry_exit_events_config:
                raise ValueError("Config not loaded")
            
            bootstrap_server = self.entry_exit_events_config["bootstrap_servers"]
            input_topic = self.entry_exit_events_config["topic"]
            
            if not bootstrap_server or not input_topic:
                raise ValueError("Invalid config for entry_exit_events")

            self.consumer = KafkaConsumer(
                input_topic,
                bootstrap_servers=bootstrap_server,
                group_id=None,
                auto_offset_reset='latest',
                enable_auto_commit=False,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
    

    def load_team_members(self):
        try: 
            self.connect_consumer()         
            if self.consumer is not None:
                for record in self.consumer:
                    message = record.value
                    event_type = message.get("event_type")
                    if event_type == "Eintritt":
                        with self.current_people_lock:
                            self.current_people_in_room.append(message["person"])
                            logging.info("Person entered the room: %s", message["person"])
                    elif event_type == "Verlassen":
                        with self.current_people_lock:
                            if message["person"] in self.current_people_in_room:
                                self.current_people_in_room.remove(message["person"])
                                logging.info("Person left the room: %s", message["person"])
        except KeyboardInterrupt:
            logging.info("load stopped.")
        finally:
            if self.consumer:
                self.consumer.close()

    def generate_random_conversation(self, sender):
        message_text = random.choice(self.conversation_messages)
        conversation_data = {   
            "sender": sender,
            "message": message_text
        }   
        return conversation_data

    def conversation_generator(self, source_name, interval_min, interval_max):
        while True:  
            if len(self.current_people_in_room) >= 2:
                selected_sender = random.choice(self.current_people_in_room)
                conversataion_data = self.generate_random_conversation(selected_sender)
                self.sender.send_single_data(source_name, conversataion_data)
            sleep_time = random.uniform(interval_min, interval_max)
            time.sleep(sleep_time)
            yield

    def send_conversation(self, source_name):
        print("OP-Teamgesprächsgenerator gestartet.")
        try:
            interval_min = self.staff_communication_config["interval_min"]
            interval_max = self.staff_communication_config["interval_max"]
            generator = self.conversation_generator(source_name, interval_min, interval_max)
            while True:
                next(generator)
        except KeyboardInterrupt:
            print("Generator gestoppt.")


if __name__ == "__main__":
    try:
        staff_communication_source_name = "staff_communication"
        entry_exit_events_source_name = "entry_exit_events"
        config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        config_loader = ConfigLoader(config_file_path)
        staff_communication_config = config_loader.load_config(staff_communication_source_name)
        entry_exit_events_config = config_loader.load_config(entry_exit_events_source_name)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        sender = SourceDataSender(staff_communication_config)
        sender.connect_producer()
        staff_generator = StaffCommunicationGenerator(entry_exit_events_config , staff_communication_config, sender)
        # Starte den Thread für load_team_members
        load_thread = Thread(target=staff_generator.load_team_members)
        load_thread.start()

        # Führe send_conversation im Hauptthread aus
        staff_generator.send_conversation(staff_communication_source_name)

        # Warten Sie darauf, dass der Thread load_team_members beendet wird
        load_thread.join()
    except Exception as e:
        logging.error("Error: %s", e)

