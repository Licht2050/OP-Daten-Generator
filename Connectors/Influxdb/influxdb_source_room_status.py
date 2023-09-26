from influxdb import InfluxDBClient
from kafka import KafkaProducer
import json

def get_room_status_from_influxdb():
    # Verbindung zur InfluxDB herstellen
    influx_client = InfluxDBClient(host='localhost', port=8086, database='environment')
    
    # InfluxDB-Abfrage
    query = 'SELECT * FROM "op_room_environment" WHERE "door_state" = \'Geschlossen\' AND time >= now() - 6h'
    
    # Abfrage ausführen
    result = influx_client.query(query)
    
    # Ergebnis in ein JSON-Format konvertieren
    room_status_data = []
    for point in result.get_points():
        room_status_data.append(point)
    
    return room_status_data

def send_to_kafka(producer, topic, data):
    for item in data:
        # Daten auf dem Bildschirm ausgeben
        # print(item)
        # Daten an Kafka senden
        producer.send(topic, value=json.dumps(item).encode('utf-8'))

if __name__ == "__main__":
    bootstrap_server = "localhost:9092"
    topic = "RoomStatus"
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)

    try:
        room_status_data = get_room_status_from_influxdb()
        send_to_kafka(producer, topic, room_status_data)
        print("Daten erfolgreich von InfluxDB zu Kafka gesendet.")
    except Exception as e:
        print("Fehler beim Senden der Daten:", e)
    finally:
        producer.close()
