

import datetime
import random


class HolidayPlace:
    """
    Represents a holiday destination with associated activities.

    Attributes:
        places (list): List of potential holiday destinations.
        activities (dict): Dictionary mapping destinations to a list of possible activities.
    """
    def __init__(self, places, activities, holiday_duration_range=(3, 14), start_date_range=(30, 180)):
        self.places = places
        self.activities = activities
        self.holiday_duration_range = holiday_duration_range
        self.start_date_range = start_date_range

    def _generate_holiday_duration(self):
        """
        Generate a random holiday duration between 3 and 14 days.

        Returns:
            int: Holiday duration in days.
        """
        return random.randint(*self.holiday_duration_range)
    
    def _generate_holiday_start_date(self):
        # Generate a random start date for the holiday within the last "start_date_range" days
        start_date = datetime.date.today() - datetime.timedelta(days=random.randint(*self.start_date_range))
        return start_date.strftime('%d.%m.%Y')  # Convert to string format
    
    def generate_holiday_place(self):
        """
        Generate a random holiday place and an associated activity.

        Returns:
            dict: Contains 'Urlaubsort' (place) and 'Aktivitaet' (activity).
        """
        place = random.choice(self.places)
        activity = random.choice(self.activities[place])
        duration = self._generate_holiday_duration()
        start_date = self._generate_holiday_start_date()
        end_date = (datetime.datetime.strptime(start_date, '%d.%m.%Y') + datetime.timedelta(days=duration)).strftime('%d.%m.%Y')
        

        holiday_place = {
            "Patient_ID": "",
            "Urlaubsort": place,
            "Aktivitaet": activity,
            "Dauer": duration,
            "Startdatum": start_date,
            "Enddatum": end_date
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

        # holiday_places_list = []
        # for place in holiday_places:
        #     activity = random.choice(self.activities[place])
        #     holiday_places_list.append({"Patient_ID": patient_id, "Urlaubsort": place, "Aktivitaet": activity})
    
        holiday_places_list = []
        for place in holiday_places:
            activity = random.choice(self.activities[place])
            duration = self._generate_holiday_duration()
            start_date = self._generate_holiday_start_date()
            end_date = (datetime.datetime.strptime(start_date, '%d.%m.%Y') + datetime.timedelta(days=duration)).strftime('%d.%m.%Y')
            holiday_places_list.append({
                "Patient_ID": patient_id, 
                "Urlaubsort": place, 
                "Aktivitaet": activity,
                "Dauer": duration,
                "Startdatum": start_date,
                "Enddatum": end_date
            })


        return holiday_places_list


