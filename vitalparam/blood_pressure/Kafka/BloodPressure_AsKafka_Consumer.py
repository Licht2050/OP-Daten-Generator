
from kafka import KafkaConsumer


def process_blood_pressure_data(data):

    systolic, diastolic = map(int, data.split(","))
    print(f"Received data: Systolic: {systolic} mmHg, Distolic {diastolic} mmHg")



def kafka_consumer(consumer):
    try:
        for message in consumer:
            data = message.value.decode()
            process_blood_pressure_data(data)
    except KeyboardInterrupt:
        print("Kafka consumer stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":

    bootstraps_server = "localhost:9092"
    topic = "Vitalparameter"



    print(f"Starting Consumer on: {bootstraps_server} in topic: {topic}...")

    
    consumer = KafkaConsumer(topic, bootstrap_servers=bootstraps_server)
    kafka_consumer(consumer)
    
