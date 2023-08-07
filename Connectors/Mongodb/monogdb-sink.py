import pymongo
from kafka import KafkaConsumer
import json

# Verbindung zur MongoDB herstellen
mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
db = mongo_client["Patientenakte"]
collection = db["Test"]

# Verbindung zum Kafka-Broker herstellen
kafka_broker = "localhost:9092"
kafka_topic = "Patientenakte"
kafka_consumer = KafkaConsumer(kafka_topic, bootstrap_servers=kafka_broker, value_deserializer=lambda v: json.loads(v.decode('utf-8')))

# Funktion zum Schreiben der Daten in die MongoDB
def write_to_mongodb(data):
    collection.insert_one(data)

# Funktion zum Verarbeiten der empfangenen Nachrichten
def process_messages():
    for message in kafka_consumer:
        data = message.value
        # Daten in MongoDB schreiben
        write_to_mongodb(data)

if __name__ == "__main__":
    try:
        # Prozess zum Verarbeiten der Nachrichten starten
        process_messages()
    except KeyboardInterrupt:
        print("Das Programm wurde beendet.")
