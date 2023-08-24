import logging
import os
import random
import time
import json
from kafka import KafkaConsumer
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender



class OPEventGenerator:
    def __init__(self, config_file_path, consumer_name , source_name):  
        self.consumer_name = consumer_name
        self.source_name = source_name
        self.consumer = None
        self.entry_probability = 0.50
        self.exit_probability = 0.50
        self.current_people_in_room = set()
        
        # Direkte Initialisierung
        self._setup_logging()
        self._load_configuration(config_file_path)
        self._setup_sender()



    def _setup_logging(self):
        """Initializes the logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _load_configuration(self, config_file_path):
        """Loads the required configurations."""
        config_loader = ConfigLoader(config_file_path)
        self.op_team_member_config = config_loader.load_config(self.consumer_name)
        self.entry_exit_events_config = config_loader.load_config(self.source_name)
    
    def _setup_sender(self):
        """Initializes the sender for data."""
        self.sender = SourceDataSender(self.entry_exit_events_config)
        self.sender.connect_producer()

    def _validate_configuration(self):
        """Validates the configurations."""
        if not all(self.op_team_member_config.get(k) for k in ["bootstrap_servers", "topic"]):
            self.logger.error("Ungültige Konfiguration für entry_exit_events")
            raise ValueError("Ungültige Konfiguration für entry_exit_events")
    
    def _initialize_consumer(self):
        """Initializes and returns a Kafka consumer."""
        return KafkaConsumer(
            self.op_team_member_config["topic"],
            bootstrap_servers=self.op_team_member_config["bootstrap_servers"],
            group_id=None,
            auto_offset_reset='latest',
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def _connect_to_consumer(self):
        """Connects to the Kafka consumer."""
        if not self.consumer:
            self._validate_configuration()
            self.consumer = self._initialize_consumer()

    def load_team(self):
        """Loads the team data from Kafka consumer."""    
        self._connect_to_consumer()
        try:
            if self.consumer:
                message_data = next(iter(self.consumer))
                team_data = message_data.value["value"]
                required_keys = ["doctors", "nurses", "anesthetists"]
                if all(key in team_data for key in required_keys):
                    self.team_members = team_data['doctors'] + team_data['nurses'] + team_data['anesthetists']
                else:
                    self.logger.error("Fehlende Schlüssel in der Nachricht")
        except StopIteration:
            self.logger.error("Keine Nachrichten im Topic gefunden")
        except json.JSONDecodeError:
            self.logger.error("Fehler beim Decodieren der Nachricht")
        except KeyError as e:
            self.logger.error(f"Fehlender Schlüssel in der Nachricht: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def send_entry_exit_events(self, entry_interval_min=1, entry_interval_max=3, event_interval_min=1, event_interval_max=3):
        self.logger.info("Generator für Eintritt/Austritts-Ereignisse gestartet.")
        try:
            # Initialphase der Betretungen ausführen
            self.perform_initial_entries(entry_interval_min, entry_interval_max)
            
            while True:
                # Zufällig entscheiden, ob eine Person den Raum betritt oder verlässt
                is_entering = random.random() < self.entry_probability
                self.handle_entry_event() if is_entering else self.handle_exit_event()
                # Warten für das nächste Ereignis
                self.wait_random_interval(event_interval_min, event_interval_max)
        except KeyboardInterrupt:
            self.logger.info("Generator gestoppt.")
    
    def perform_initial_entries(self, interval_min, interval_max):
        self.logger.info("Start der initialen Betretungen")
        for person in self.team_members:
            self._send_event_for_person(person, entering=True)
            self.wait_random_interval(interval_min, interval_max)
            self.current_people_in_room.add(person)
        self.logger.info("Initialen Betretungen abgeschlossen")


    def get_available_people(self):
        """Returns the set of people who are not in the room."""
        return set(self.team_members) - self.current_people_in_room

    def handle_entry_event(self):
        available_people = self.get_available_people()
        if available_people:
            person = random.choice(list(available_people))
            self.current_people_in_room.add(person)
            # Eintrittsereignis senden
            self._send_event_for_person(person, entering=True)

    def handle_exit_event(self):
        # Überprüfen, ob sich noch Personen im Raum befinden
        if self.current_people_in_room:
            person = random.choice(list(self.current_people_in_room))
            self.current_people_in_room.remove(person)
            # Verlassenereignis senden
            self._send_event_for_person(person, entering=False)

    def _send_event_for_person(self, person, entering):
        event = self.generate_entry_exit_event(person, entering)
        self.sender.send_single_data(self.source_name, event)

    def generate_entry_exit_event(self, person, entering):
        event_type = "Eintritt" if entering else "Verlassen"
        return {
            "person": person,
            "event_type": event_type,
        }

    def wait_random_interval(self, interval_min, interval_max):
        interval = random.randint(interval_min, interval_max)
        time.sleep(interval)
     


if __name__ == "__main__":

    consumer_name = "op_team"
    source_name = "entry_exit_events"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')

    op_generator = OPEventGenerator(config_file_path, consumer_name , source_name)
    op_generator.load_team()
    
    op_generator.send_entry_exit_events()