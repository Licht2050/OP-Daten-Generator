import time
import random
from kafka import KafkaConsumer
from influxdb import InfluxDBClient

def write_to_influxdb(data):
    # Verbindung zur InfluxDB herstellen
    influxdb_host = "localhost"
    influxdb_port = 8086
    influxdb_database = "environment"
    influxdb_client = InfluxDBClient(host=influxdb_host, port=influxdb_port, database=influxdb_database)

    # Messdaten aus der empfangenen Nachricht extrahieren
    door_state = data["Türzustand"]
    temperature = data["Raumtemperatur"]
    humidity = data["Luftfeuchtigkeit"]
    pressure = data["Luftdruck"]
    illumination = data["Bleuchtungsstärke"]

    # Datenpunkt für InfluxDB erstellen
    json_body = [
        {
            "measurement": "op_room_environment",
            "fields": {
                "door_state": door_state,
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure,
                "illumination": illumination
            }
        }
    ]

    # Datenpunkt in InfluxDB schreiben
    influxdb_client.write_points(json_body)

def consume_from_kafka(bootstrap_server, topic):
    # Kafka-Consumer erstellen
    consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_server, value_deserializer=lambda x: x.decode('utf-8'))

    try:
        for message in consumer:
            # Empfangene Nachricht von Kafka verarbeiten
            data = eval(message.value)  # In diesem Fall wird eval verwendet, um den String in ein Python-Dict umzuwandeln
            write_to_influxdb(data)
    except KeyboardInterrupt:
        print("Kafka-Consumer gestoppt.")
    except Exception as e:
        print("Fehler beim Verarbeiten der Nachricht:", e)
    finally:
        consumer.close()

if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    topic = "RoomStatus"

    try:
        consume_from_kafka(bootstrap_server, topic)
    except Exception as e:
        print("Error: {e}")
