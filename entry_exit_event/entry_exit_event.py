import random
import time
import json
from kafka import KafkaProducer, KafkaConsumer
import sys
sys.path.append('../help_funktions')
from send_to_kafka import send_to_topic
from kafka import KafkaConsumer

class OPEventGenerator:
    def __init__(self, bootstrap_server, team_member_topic, entry_exit_topic):
        self.bootstrap_server = bootstrap_server
        self.team_member_topic = team_member_topic
        self.entry_exit_topic = entry_exit_topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
        self.entry_probability = 0.95
        self.exit_probability = 0.05
        self.current_people_in_room = set()

    def load_team(self):
        consumer = KafkaConsumer(
            self.team_member_topic,
            bootstrap_servers=self.bootstrap_server,
        )
        team_message = next(consumer)
        team_data = json.loads(team_message.value.decode('utf-8'))
        self.team_members = team_data['doctors'] + team_data['nurses'] + team_data['anesthetists']
        
    def generate_entry_exit_event(self, person, entering):
        event_type = "betritt den OP-Saal." if entering else "verlässt den OP-Saal."
        return f"{person} {event_type}"
    
    def send_entry_exit_events(self, interval_min=1, interval_max=3):
        print("Generator für Eintritt/Austritts-Ereignisse gestartet.")
        try:
            # Initial entries
            for person in self.team_members:
                event_enter = self.generate_entry_exit_event(person, True)
                send_to_topic(self.producer, self.entry_exit_topic, event_enter)
                sleep_time = random.randint(interval_min, interval_max)
                time.sleep(sleep_time)
            while True:
                entering = random.random() < self.entry_probability
                if entering:
                    if len(self.current_people_in_room) < len(self.team_members):
                        available_people = set(self.team_members) - self.current_people_in_room
                        person = random.choice(list(available_people))
                        self.current_people_in_room.add(person)
                    else:
                        continue
                else:
                    if self.current_people_in_room:
                        person = random.choice(list(self.current_people_in_room))
                        self.current_people_in_room.remove(person)
                    else:
                        continue
                event = self.generate_entry_exit_event(person, entering)
                send_to_topic(self.producer, self.entry_exit_topic, event)
                interval_min, interval_max = min(interval_min, interval_max), max(interval_min, interval_max)        
                sleep_time = random.randint(interval_min, interval_max)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("Generator gestoppt.")
        finally:
            self.producer.flush()

if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    team_member_topic = "OPTeam"
    entry_exit_topic = "OP_Entry_Exit_Events"
    
    op_generator = OPEventGenerator(bootstrap_server, team_member_topic, entry_exit_topic)
    op_generator.load_team()
    print (op_generator.team_members)
    op_generator.send_entry_exit_events()
