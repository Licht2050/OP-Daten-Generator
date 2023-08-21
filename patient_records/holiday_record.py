

import random


class HolidayPlace:
    def __init__(self):
        self.places = [
            "Paris", "Malediven", "New York City", "Trolltunga", 
            "Grand Canyon", "Sambia und Malawi", "Botswana und Simbabwe",
            "Bali", "Dschungel-Bungalows an der Nordküste"
        ]

        self.acivities = {
            "Grand Canyon": ["Wandern", "Campingtouren", "Skywalk"],
            "Trolltunga": ["Campingtouren", "Spaziergänge"],
            "New York City": ["Times Square besucht", "Broadway-Show gesehen", "Central Park erkundet"],
            "Paris": ["Eiffelturm besichtigt", "Louvre Museum besucht"],
            "Malediven": ["Strandspaziergang gemacht", "Schnorcheln", "Tauchen"],
            "Tokio": ["Asakusa Tempel besichtigt", "Shinjuku Gyoen Park besucht", "Sushi gegessen"],
            "Bali": ["Wandern", "Buschwanderungen", "Wildbeobachtung zu Fuß"],
            "Sambia und Malawi": ["Abenteuerliche Kanufahrt", "Wildbeobachtung zu Fuß", "Schnorcheln"],
            "Botswana und Simbabwe": ["Pirschfahrt", "Buschwanderungen", "Helikopterflug", "Wild Water Rafting", "Bungee Jumping"],
            "Dschungel-Bungalows an der Nordküste": ["Wandern"]
        }

    def generate_holiday_place(self):
        place = random.choice(self.places)
        activity = random.choice(self.acivities[place])

        holiday_place = {
            "Urlaubsort": place,
            "Aktivitaet": activity
        }
        return holiday_place

    def generate_random_holiday_places(self, num_places):
        all_places = self.places.copy()
        holiday_places = random.sample(all_places, min(len(all_places), num_places))

        holiday_places_list = []
        for place in holiday_places:
            activity = random.choice(self.acivities[place])
            holiday_places_list.append({"Urlaubsort": place, "Aktivitaet": activity})

        return holiday_places_list



    
    # def print_holiday_place(self, holiday_place):
    #     for key, value in holiday_place.items():   
    #             print(f"{key}: {value}")
    
# def send_holidy_place(producer, topic , interval=5):
#     generator = HolidayPlace()
#     print("Urlaubsort und Aktivität:")
#     try:
#         while True:
#             urlaubsort = generator.generate_holiday_place()
#             generator.print_holiday_place(urlaubsort)
#             message = json.dumps(urlaubsort)
#             producer.send(topic, value=str(message).encode('utf-8'))
#             time.sleep(interval)
#     except KeyboardInterrupt:
#         print("Generator stopped.")
#     finally:
#         producer.flush()
    
# if __name__ == "__main__":
#     bootstrap_server = "localhost:9092"
#     topic = "Patientenakte"
#     producer = KafkaProducer(bootstrap_servers=bootstrap_server)

#     try:
#         send_holidy_place(producer, topic)
#     except Exception as e:
#         print("Error: {e}")
#     finally:
#         producer.close()
