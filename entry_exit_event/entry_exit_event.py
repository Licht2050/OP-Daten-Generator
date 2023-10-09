import logging
import os
import random
import time
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH, OP_DETAILS_NAME, OP_RECORD_PATH, OP_TEAM_INFO_NAME, OP_TEAM_INFO_PATH, REQUIRED_TEAM_KEYS, ENTRY_EXIT_EVENT_SOURCE_NAME
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender




class OPEventGenerator:
    def __init__(self, config_file_path, op_team_info_path, consumer_name , source_name, op_record_path, op_details_name):  
        self.consumer_name = consumer_name
        self.source_name = source_name
        self.consumer = None
        self.entry_probability = 0.50
        self.exit_probability = 0.50
        self.current_people_in_room = set()
        
        # Direkte Initialisierung
        self._setup_logging()
        self._load_configuration(config_file_path, op_team_info_path, op_record_path, op_details_name)
        self._setup_sender()



    def _setup_logging(self):
        """Initializes the logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _load_configuration(self, config_file_path, op_team_info_path, op_record_path, op_details_name):
        """Loads the required configurations."""
        op_record_config_loader = ConfigLoader(op_record_path)
        self.op_record_config = op_record_config_loader.load_config(op_details_name)

        config_loader = ConfigLoader(config_file_path)
        self.entry_exit_events_config = config_loader.load_config(self.source_name)

        op_team_info_config_loader = ConfigLoader(op_team_info_path)
        self.op_team_member_config = op_team_info_config_loader.load_config(self.consumer_name)
    
    def _setup_sender(self):
        """Initializes the sender for data."""
        self.sender = SourceDataSender(self.entry_exit_events_config)
        self.sender.connect_producer()

    def load_team(self):
        """Loads the team data from Json file."""    
        missing_keys = [key for key in REQUIRED_TEAM_KEYS if key not in self.op_team_member_config]
        if missing_keys:
            self.logger.error(f"Fehlende Schlüssel in der Nachricht: {', '.join(missing_keys)}")
            raise ValueError(f"Fehlende Schlüssel in der Konfiguration: {', '.join(missing_keys)}")

        self.team_members = sum((self.op_team_member_config[key] for key in REQUIRED_TEAM_KEYS), [])


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
        """Generates and sends the event for a person entering or exiting."""
        event = {
            "op_room": self.op_record_config["Operation_Room"],
            "person": person,
            "event": "Eintritt" if entering else "Verlassen",
        }
        self.sender.send_single_data(self.source_name, event)

    def wait_random_interval(self, interval_min, interval_max):
        """Waits for a random interval between the given min and max values."""
        interval = random.randint(interval_min, interval_max)
        time.sleep(interval)
     


if __name__ == "__main__":

    op_generator = OPEventGenerator(CONFIG_FILE_PATH, OP_TEAM_INFO_PATH, OP_TEAM_INFO_NAME , ENTRY_EXIT_EVENT_SOURCE_NAME, OP_RECORD_PATH, OP_DETAILS_NAME)
    op_generator.load_team()
    
    op_generator.send_entry_exit_events()