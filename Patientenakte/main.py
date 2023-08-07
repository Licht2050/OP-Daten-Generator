from kafka import KafkaProducer
from patient_data_generator import generate_patient_data, send_patient_data

if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    topic = "Patientenakte"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        send_patient_data(producer, topic)
    except Exception as e:
        print("Error:", e)
    finally:
        producer.close()