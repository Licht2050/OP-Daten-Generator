import asyncio
import pymongo
from kafka import KafkaProducer
import json
from bson import Timestamp

# Verbindung zum Kafka-Broker herstellen
kafka_broker = "localhost:9092"
kafka_topic = "Patientenakte"
kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker, value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'))

async def send_to_kafka(data):
    kafka_producer.send(kafka_topic, value=data)

async def watch_change_stream():
    # Verbindung zur MongoDB herstellen
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = mongo_client["Patientenakte"]
    collection = db["Test"]

    pipeline = [{"$match": {"operationType": {"$in": ["insert", "update", "replace", "delete"]}}}]

    with collection.watch(pipeline) as stream:
        for change in stream:
            # Timestamp in ein Python-Datumsobjekt umwandeln
            if isinstance(change["clusterTime"], Timestamp):
                change["clusterTime"] = change["clusterTime"].as_datetime()

            # Änderungen an Kafka senden
            await send_to_kafka(change)

async def main():
    try:
        # Watcher für den Change Stream starten
        await watch_change_stream()
    except KeyboardInterrupt:
        print("Das Programm wurde beendet.")
    except Exception as e:
        print("Fehler beim Lesen des Change Streams:", e)

if __name__ == "__main__":
    asyncio.run(main())
