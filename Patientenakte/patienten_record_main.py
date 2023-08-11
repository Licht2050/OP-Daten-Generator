from kafka import KafkaProducer
from patient_data_generator import generate_patient_data, send_patient_data

if __name__ == "__main__":
    bootstrap_server = "192.168.29.120:9094"
    topic = "patientendaten"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        send_patient_data(producer, topic)
    except Exception as e:
        print("Error:", e)
    finally:
        producer.close()