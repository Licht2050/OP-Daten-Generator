import logging
import os
import random
import time
import json
import sys
from kafka import KafkaConsumer
from threading import Lock, Thread

# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from source_data_sender import SourceDataSender
from config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
STAFF_COMMUNICATION_SOURCE = "staff_communication"
ENTRY_EXIT_EVENTS_SOURCE = "entry_exit_events"


class StaffCommunicationGenerator:
    """
    A generator that simulates staff communications based on entry and exit events.
    Listens for entry and exit events from a Kafka topic and generates random conversation messages.
    """
    def __init__(self, entry_exit_events_config , staff_communication_config, sender):
        """
        Initialize the generator with configurations and a sender.
        
        :param entry_exit_events_config: Configuration related to entry and exit events.
        :param staff_communication_config: Configuration related to staff communication.
        :param sender: Object responsible for sending messages.
        """
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
        """
        Connect to the Kafka consumer. If already connected, the method simply returns.
        If the configuration does not contain required values, it raises a ValueError.
        """
        if self.consumer:
            return

        bootstrap_server = self.entry_exit_events_config.get("bootstrap_servers")
        input_topic = self.entry_exit_events_config.get("topic")
            
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
    
    def handle_entry_event(self, message):
        """
        Handle an entry event from the Kafka topic. It adds the person to the current_people_in_room list.
        
        :param message: The entry event message from the Kafka topic.
        """
        with self.current_people_lock:
            self.current_people_in_room.append(message["person"])
            logging.info("Person entered the room: %s", message["person"])

    def handle_exit_event(self, message):
        """
        Handle an exit event from the Kafka topic. It removes the person from the current_people_in_room list.
        
        :param message: The exit event message from the Kafka topic.
        """
        with self.current_people_lock:
            if message["person"] in self.current_people_in_room:
                self.current_people_in_room.remove(message["person"])
                logging.info("Person left the room: %s", message["person"])

    def load_team_members(self):
        """
        Load team members from the Kafka topic. It listens for entry and exit events and updates the current_people_in_room list.
        """
        event_handlers = {
            "Eintritt": self.handle_entry_event,
            "Verlassen": self.handle_exit_event
        }

        self.connect_consumer() 
        try:         
            if self.consumer is not None:
                for record in self.consumer:
                    message = record.value
                    event_type = message.get("event_type")
                    handler = event_handlers.get(event_type)
                    if handler:
                        handler(message)
        except KeyboardInterrupt:
            logging.info("load stopped.")
        finally:
            if self.consumer:
                self.consumer.close()

    def generate_random_conversation(self, sender):
        """
        Generate a random conversation message for a given sender.
        
        :param sender: The person sending the message.
        :return: A dictionary containing the sender and the generated message.
        """
        return {   
            "sender": sender,
            "message": random.choice(self.conversation_messages)
        }   


    def conversation_generator(self, source_name, interval_min, interval_max):
        """
        Generate random conversations for a given source.

        :param source_name: The name of the source.
        :param interval_min: The minimum interval between two conversations.
        :param interval_max: The maximum interval between two conversations.
        """
        while True:  
            if len(self.current_people_in_room) >= 2:
                selected_sender = random.choice(self.current_people_in_room)
                conversataion_data = self.generate_random_conversation(selected_sender)
                self.sender.send_single_data(source_name, conversataion_data)
            sleep_time = random.uniform(interval_min, interval_max)
            time.sleep(sleep_time)
            yield

    def send_conversation(self, source_name):
        """
        Send conversations for a given source.
        """
        print("OP-Teamgesprächsgenerator gestartet.")
        try:
            interval_min = self.staff_communication_config["interval_min"]
            interval_max = self.staff_communication_config["interval_max"]
            generator = self.conversation_generator(source_name, interval_min, interval_max)
            while True:
                next(generator)
        except KeyboardInterrupt:
            print("Generator gestoppt.")


def main():
    """
    The main function.
    """
    try:
        # Load configurations
        config_loader = ConfigLoader(CONFIG_PATH)
        staff_communication_config = config_loader.load_config(STAFF_COMMUNICATION_SOURCE)
        entry_exit_events_config = config_loader.load_config(ENTRY_EXIT_EVENTS_SOURCE)
        
        
        # Initialize and connect sender
        sender = SourceDataSender(staff_communication_config)
        sender.connect_producer()

        # Initialize staff generator and start processing
        staff_generator = StaffCommunicationGenerator(entry_exit_events_config , staff_communication_config, sender)

        # Start loading team members in a separate thread
        load_thread = Thread(target=staff_generator.load_team_members)
        load_thread.start()

        # Generate and send conversations in the main thread
        staff_generator.send_conversation(STAFF_COMMUNICATION_SOURCE)

        # Wait for the load thread to finish
        load_thread.join()
    except Exception as e:
        logging.error("Error: %s", e)

if __name__ == "__main__":
    main()    

