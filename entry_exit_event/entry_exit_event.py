import datetime
import random
import time
import json
from kafka import KafkaProducer, KafkaConsumer
import sys
sys.path.append('../help_classes_and_functions')
from send_to_kafka import send_to_topic
from kafka import KafkaConsumer



class OPEventGenerator:
    def __init__(self, bootstrap_server, team_member_topic, entry_exit_topic):
        self.bootstrap_server = bootstrap_server
        self.team_member_topic = team_member_topic
        self.entry_exit_topic = entry_exit_topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
        self.entry_probability = 0.50
        self.exit_probability = 0.50
        self.current_people_in_room = set()

    def load_team(self):
        consumer = KafkaConsumer(
            self.team_member_topic,
            bootstrap_servers=self.bootstrap_server,
        )
        team_message = next(consumer)
        team_data = json.loads(team_message.value.decode('utf-8'))
        self.team_members = team_data['doctors'] + team_data['nurses'] + team_data['anesthetists']
        
   
    
    def send_entry_exit_events(self, entry_interval_min=1, entry_interval_max=3, event_interval_min=1, event_interval_max=3):
        print("Generator für Eintritt/Austritts-Ereignisse gestartet.")
        try:
            # Initialphase der Betretungen ausführen
            self.perform_initial_entries(entry_interval_min, entry_interval_max)
            
            while True:
                # Zufällig entscheiden, ob eine Person den Raum betritt oder verlässt
                entering = random.random() < self.entry_probability
                
                if entering:
                    # Behandeln des Betretungsereignisses
                    self.handle_entry_event()
                else:
                    # Behandeln des Verlassensereignisses
                    self.handle_exit_event()
                # Warten für das nächste Ereignis
                self.wait_random_interval(event_interval_min, event_interval_max)
        except KeyboardInterrupt:
            print("Generator gestoppt.")
        finally:
            self.producer.flush()

    def perform_initial_entries(self, interval_min, interval_max):
        print("Start der initialen Betretungen")
        for person in self.team_members:
            self.send_entry_exit_event(person, True)
            self.wait_random_interval(interval_min, interval_max)
            self.current_people_in_room.add(person)
        print("Initialen Betretungen abgeschlossen")


    def handle_entry_event(self):
        # Überprüfen, ob sich noch Personen ausserhalb des Raums befinden
        if len(self.current_people_in_room) < len(self.team_members):
            available_people = set(self.team_members) - self.current_people_in_room
            person = random.choice(list(available_people))
            self.current_people_in_room.add(person)
            # Eintrittsereignis senden
            self.send_entry_exit_event(person, True)

    def handle_exit_event(self):
        # Überprüfen, ob sich noch Personen im Raum befinden
        if self.current_people_in_room:
            person = random.choice(list(self.current_people_in_room))
            self.current_people_in_room.remove(person)
            # Verlassenereignis senden
            self.send_entry_exit_event(person, False)


    def generate_entry_exit_event(self, person, entering):
        event_type = "Eintritt" if entering else "Verlassen"
        event_data = {
            "person": person,
            "event_type": event_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return event_data    

    def send_entry_exit_event(self, person, entering):
        event = self.generate_entry_exit_event(person, entering)
        send_to_topic(self.producer, self.entry_exit_topic, event)

    def wait_random_interval(self, interval_min, interval_max):
        interval = random.randint(interval_min, interval_max)
        time.sleep(interval)

     


if __name__ == "__main__":
    bootstrap_server = "192.168.29.120:9093"
    team_member_topic = "op_team"
    entry_exit_topic = "ein_ausgangsereignisse"
    
    op_generator = OPEventGenerator(bootstrap_server, team_member_topic, entry_exit_topic)
    op_generator.load_team()
    print (op_generator.team_members)
    op_generator.send_entry_exit_events()
