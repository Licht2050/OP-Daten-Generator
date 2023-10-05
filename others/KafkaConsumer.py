
import json
from kafka import KafkaConsumer



def kafka_consumer(consumer):
    try:
        for message in consumer:
            data = json.loads(message.value.decode('utf-8'))
            print(data)
    except KeyboardInterrupt:
        print("Kafka consumer stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":

    bootstraps_server = "localhost:9092"
    # topic = "patient_data"
    # topic = "environmental_data"
    topic = "vital_parameters"
    # topic = "entry_exit_events"
    # topic = "indoor_environment_data"
    # topic = "operation_team"
    # topic = "staff_communication"
    # topic = "operation_record"
    # topic = "patient_entry_exit_events"

    print(f"Starting Consumer on: {bootstraps_server} in topic: {topic}...")

    
    consumer = KafkaConsumer(
        topic, 
        bootstrap_servers=bootstraps_server,

        auto_offset_reset='earliest',

        )
    kafka_consumer(consumer)
    
