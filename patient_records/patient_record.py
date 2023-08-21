

import random
import time
import csv
import os


class PatientRecordGenerator:
    def __init__(self):
        self.patient_ids = set()
        self.names = ["Müller", "Bäcker", "Schmidt", "Schneider", "Hoffman", "Ajadi", "Weber", "Fischer", "Meyer", "Maier", "Kraus", "Herrmann"]
        self.male_names = [ "Hans", "Karl", "Walter", "Kurt", "Friedrich", "Fritz", "Heinrich"]
        self.female_names = ["Maria", "Elisabeth", "Ruth", "Hilde", "Eva", "charlotte", "Erika"]
        self.genders= ["weiblich", "männlich"]
        self.streets = ["Banhofstraße 1", "Goebenstraße 40", "Am Rastpfuhl 3", "St. Johanner Str.", "Breite Str."]
        self.cities = ["Saarbreucken"]
        self.postal_codes = [66113, 66117, 6123, 66111]
        self.blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"]
        self.weight_range = (45, 120)
        self.height_range = (140, 195)
        self.load_existing_ids()

        # ...

    def load_existing_ids(self):
        try:
            with open('patient_ids.csv', 'r') as file:
                reader = csv.reader(file)
                existing_ids = set(row[0] for row in reader)
            return existing_ids
        except FileNotFoundError:
            return set()
        
    def save_new_id(self, patient_id):
        try:
            mode = 'a' if os.path.exists('patient_ids.csv') else 'w'
            with open('patient_ids.csv', mode) as file:
                writer = csv.writer(file)
                writer.writerow([patient_id])
        except Exception as e:
            print("Error:", e)   


    def generate_random_birth_date(slef):
        now = int(time.time())
        #Geburtsdatum in den letzten drei Jahren
        ten_years_ago = now - (365 * 24 * 60 * 60 * 10)
        birth_date = time.strftime("%d.%m.%Y", time.localtime(random.randint(ten_years_ago, now)))
        return birth_date

    def generate_random_patient_id(self):
        # Lade vorhandene Patienten-IDs aus der CSV-Datei
        existing_ids = self.load_existing_ids()
        # Generiere eine zufällige 6-stellige ID und überprüfe, ob sie bereits existiert
        while True:
            patient_id = str(random.randrange(100000, 1000000))
            if patient_id not in existing_ids:
                self.save_new_id(patient_id)
                return patient_id

    def generate_random_patient_record(self):  
        patient_id = self.generate_random_patient_id()
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
            "Patient_ID": patient_id,
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
    

# def send_patient_record(producer, topic, interval=5):
#     generator = PatientRecordGenerator()

#     try:
#         while True:
#             patient_record = generator.generate_random_patient_record()
#             message = f"{patient_record}"

#             producer.send(topic, value=str(message).encode('utf-8'))
#             print(patient_record)
#             time.sleep(interval)
#     except KeyboardInterrupt:
#         print("Patient record generator stopped.")
#     finally:
#         producer.flush()

# if __name__ == "__main__":

#     bootstrap_server = "localhost:9092"
#     topic = "Patientenakte"

#     producer = KafkaProducer(bootstrap_servers= bootstrap_server)
#     try:
#         send_patient_record(producer, topic)
#     except Exception as e:
#         print("Error: {e}")
#     finally:
#         producer.close()
    


