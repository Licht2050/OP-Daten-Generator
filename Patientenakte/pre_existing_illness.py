

import time
import random
from kafka import KafkaProducer


class PreExistingIllness:
    def __init__(self):
        self.illnesses = [
            "Herzinsuffizienz", "Schlaganfall", "Herzinfarkt", "Lungenembolie",
            "Nierenversagen", "Diabetes mellitus", "Asthma", "Bluthochdruck"
        ]
        self.treatments = ["Medikamente", "Operation", "Physiotherapie", "Dialyse"]
        self.diagnosed_range = (360*24*60*60*3, 360*24*60*60*15) # 3 bis 15 Jahre zurück
        self.treated_range = (360*24*60*60*1, 360*24*60*60*6) # 1 bis 6 Jahre zurück

    def generate_random_diagnose_date(self):
        now = int(time.time())
        three_years_ago = now - self.diagnosed_range[0]
        fifteen_years_ago = now - self.diagnosed_range[1]
        diagnos_date = time.strftime("%d.%m.%Y", time.localtime(random.randint(fifteen_years_ago, three_years_ago)))
        return diagnos_date
    
    def generate_random_treated_date(self, diagnosed_date):
        diagnosed_timestamp = int(time.mktime(time.strptime(diagnosed_date, "%d.%m.%Y")))
        one_year_after_diagnose = diagnosed_timestamp + self.treated_range[0]
        six_years_after_diagnose = diagnosed_timestamp + self.treated_range[1]
        treated_date = time.strftime("%d.%m.%Y", time.localtime(random.randint(one_year_after_diagnose, six_years_after_diagnose)))
        return treated_date
    
    def generate_random_pre_existing_illness(self):
        pre_existing_illness = random.choice(self.illnesses)
        diagnosed_date = self.generate_random_diagnose_date()
        treatment = random.choice(self.treatments)
        treated_date = self.generate_random_treated_date(diagnosed_date)

        pre_existing_illness_record = {
            "Vorerkrankung": pre_existing_illness,
            "Diagnosedatum": diagnosed_date,
            "Behandlung": treatment,
            "Behandlungsdatum": treated_date,
            "Weitere Informationen": "..."
        }

        return pre_existing_illness_record
    
    def generate_random_pre_existing_illness(self, num_illnesses):
        all_illnesses = self.illnesses.copy()
        pre_existing_illnesses = random.sample(all_illnesses, min(len(all_illnesses), num_illnesses))

        illness_records = []
        for pre_existing_illness in pre_existing_illnesses:
            diagnosed_date = self.generate_random_diagnose_date()
            treatment = random.choice(self.treatments)
            treated_date = self.generate_random_treated_date(diagnosed_date)

            illness_record = {
                "Vorerkrankung": pre_existing_illness,
                "Diagnosedatum": diagnosed_date,
                "Behandlung": treatment,
                "Behandlungsdatum": treated_date,
                "Weitere Informationen": "..."
            }
            illness_records.append(illness_record)

        return illness_records


    # def generate_random_pre_existing_illnesses(self):
    #     num_illnesses = random.randint(0, 5)  # Zufällige Anzahl von Vorerkrankungen (0 bis 5)
    #     pre_existing_illnesses = []
    #     for _ in range(num_illnesses):
    #         pre_existing_illness = random.choice(self.illnesses)
    #         diagnosed_date = self.generate_random_diagnose_date()
    #         treatment = random.choice(self.treatments)
    #         treated_date = self.generate_random_treated_date(diagnosed_date)

    #         pre_existing_illness_record = {
    #             "Vorerkrankung": pre_existing_illness,
    #             "Diagnosedatum": diagnosed_date,
    #             "Behandlung": treatment,
    #             "Behandlungsdatum": treated_date,
    #             "Weitere Informationen": "..."
    #         }
    #         pre_existing_illnesses.append(pre_existing_illness_record)
    #     return pre_existing_illnesses




    
# def send_patient_pre_existing_illness(producer, topic, interval=5):
#     generator = PreExistingIllness()

#     try:
#         while True:
#             pre_existing_illness = generator.generate_random_pre_existing_illness()
#             message = f"{pre_existing_illness}"
#             producer.send(topic, value=str(message).encode("utf-8"))
#             print(pre_existing_illness)
#             time.sleep(5)
#     except KeyboardInterrupt:
#         print("Pre-existing illness generator stopped.")
#     finally:
#         producer.flush()

# if __name__ == "__main__":
#     bootstrap_server = "localhost:9092"
#     topic = "Patientenakte"

#     producer = KafkaProducer(bootstrap_servers=bootstrap_server)
#     try:
#         send_patient_pre_existing_illness(producer, topic)
#     except Exception as e:
#         print("Error: {e}")
#     finally:
#         producer.close()