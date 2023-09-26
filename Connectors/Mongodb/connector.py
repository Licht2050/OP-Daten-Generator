from kafka import KafkaProducer
from pymongo import MongoClient
from bson import ObjectId 
import json

# MongoDB-Konfiguration
mongo_uri = "mongodb://localhost:27017"
mongo_db = "Patientenakte"
mongo_collection = "Test"

# Kafka-Producer-Konfiguration
kafka_broker = "localhost:9092"
kafka_topic = "Patientenakte"

# Verbindung zu MongoDB herstellen
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[mongo_db]
mongo_collection = mongo_db[mongo_collection]

# Kafka-Producer initialisieren
kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker,
                               value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'))  # Benutzerdefinierte Serializer-Funktion

# Funktion zum Senden von Daten an Kafka
def send_to_kafka(data):
    kafka_producer.send(kafka_topic, value=data)
    kafka_producer.flush()

# Daten von MongoDB abrufen und an Kafka senden
for document in mongo_collection.find():
    # MongoDB ObjectId in String konvertieren, bevor es an Kafka gesendet wird
    document['_id'] = str(document['_id'])
    send_to_kafka(document)

# Kafka-Producer und MongoDB-Verbindung schließen
kafka_producer.close()
mongo_client.close()
