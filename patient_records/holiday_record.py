

import random


class HolidayPlace:
    """
    Represents a holiday destination with associated activities.

    Attributes:
        places (list): List of potential holiday destinations.
        activities (dict): Dictionary mapping destinations to a list of possible activities.
    """
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
        """
        Generate a random holiday place and an associated activity.

        Returns:
            dict: Contains 'Urlaubsort' (place) and 'Aktivitaet' (activity).
        """
        place = random.choice(self.places)
        activity = random.choice(self.acivities[place])

        holiday_place = {
            "Patient_ID": "",
            "Urlaubsort": place,
            "Aktivitaet": activity
        }
        return holiday_place

    def generate_random_holiday_places(self, num_places, patient_id):
        """
        Generate a list of random holiday places and their associated activities.

        Args:
            num_places (int): Number of holiday places to generate.

        Returns:
            list: List of dictionaries containing 'Urlaubsort' and 'Aktivitaet'.
        """
        all_places = self.places.copy()
        holiday_places = random.sample(all_places, min(len(all_places), num_places))

        holiday_places_list = []
        for place in holiday_places:
            activity = random.choice(self.acivities[place])
            holiday_places_list.append({"Patient_ID": patient_id, "Urlaubsort": place, "Aktivitaet": activity})

        return holiday_places_list


