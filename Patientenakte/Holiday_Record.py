

import time
import random

class HolidyPlace:
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

    def generate_holidy_place(self):
        place = random.choice(self.places)
        activity = random.choice(self.acivities[place])

        holidy_place = {
            "Urlaubsort": place,
            "Aktivität": activity
        }
        return holidy_place
    
if __name__ == "__main__":
    generator = HolidyPlace()

    try:
        while True:
            urlaubsort = generator.generate_holidy_place()
            print("Urlaubsort und Aktivität:")
            for key, value in urlaubsort.items():
                print(f"{key}: {value}")
            input("Press Enter to continue...")
    except KeyboardInterrupt:
        print("Generator stopped.")