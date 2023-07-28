

import random
import time

class PatientRecordGenerator:
    def __init__(self):
        self.names = ["Müller", "Bäcker", "Schmidt", "Schneider", "Hoffman", "Ajadi", "Weber", "Fischer", "Meyer", "Maier", "Kraus", "Herrmann"]
        self.male_names = [ "Hans", "Karl", "Walter", "Kurt", "Friedrich", "Fritz", "Heinrich"]
        self.female_names = ["Maria", "Elisabeth", "Ruth", "Hilde", "Eva", "charlotte", "Erika"]
        self.genders= ["weiblich", "männlich"]
        self.streets = ["Banhofstraße 1", "Goebenstraße 40", "Am Rastpfuhl 3", "St. Johanner Str.", "Breite Str."]
        self.cities = ["Saarbrücken"]
        self.postal_codes = [66113, 66117, 6123, 66111]
        self.blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"]
        self.weight_range = (45, 120)
        self.height_range = (140, 195)

    def generate_random_birth_date(slef):
        now = int(time.time())
        #Geburtsdatum in den letzten drei Jahren
        ten_years_ago = now - (365 * 24 * 60 * 60 * 10)
        birth_date = time.strftime("%d.%m.%Y", time.localtime(random.randint(ten_years_ago, now)))
        return birth_date


    def generate_random_patient_record(self):  
        gender = random.choice(self.genders)
        if gender == "weiblich":
            first_name = random.choice(self.female_names)
        else:
            first_name = random.choice(self.male_names)

        last_name = random.choice(self.names)
        full_name = f"{first_name} {last_name}"

        
        street = random.choice(self.streets)
        city = random.choice(self.cities)
        postal_code = random.choice(self.postal_codes)

        blood_group = random.choice(self.blood_groups)
        weight = random.randint(*self.weight_range)
        height = random.randint(*self.height_range)
        birth_date = self.generate_random_birth_date()

        patient_record = {
            "Name": last_name,
            "Vorname": first_name,
            "Geschlecht": gender,
            "Geburtsdatum": birth_date,
            "Straße": street,
            "Stadt": city,
            "Postleitzahl": postal_code,
            "Blutgruppe": blood_group,
            "Gewicht": weight,
            "Größe": height 
        }

        return patient_record
    

if __name__ == "__main__":
    generator = PatientRecordGenerator()

    try:
        while True:
            patient_record = generator.generate_random_patient_record()
            print(patient_record)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Patient record generator stopped.")


