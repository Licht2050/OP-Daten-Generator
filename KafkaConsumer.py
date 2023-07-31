
from kafka import KafkaConsumer



def kafka_consumer(consumer):
    try:
        for message in consumer:
            data = message.value.decode('utf-8')
            print(data)
    except KeyboardInterrupt:
        print("Kafka consumer stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":

    bootstraps_server = "localhost:9092"
    topic = "Patientenakte"



    print(f"Starting Consumer on: {bootstraps_server} in topic: {topic}...")

    
    consumer = KafkaConsumer(topic, bootstrap_servers=bootstraps_server)
    kafka_consumer(consumer)
    
