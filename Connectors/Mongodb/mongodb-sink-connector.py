import subprocess
import os

def run_kafka_connector():
    # Befehl zum Starten des Kafka-Connectors im Standalone-Modus.
    command = "/usr/local/kafka/bin/connect-standalone.sh /usr/local/kafka/config/connect-standalone.properties /usr/local/kafka/plugins/mongodb-sink.properties"
    
    # Setze den Pfad zur Log-Datei
    log_file_path = os.path.join(os.getcwd(), "connector.log")
    
    # Starte den Kafka-Connector im Hintergrund und leite die Ausgabe in die Log-Datei um.
    with open(log_file_path, "w") as log_file:
        subprocess.Popen(command, shell=True, stdout=log_file, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    print("Starte Kafka Connector im Hintergrund...")
    run_kafka_connector()
    print("Kafka Connector läuft im Hintergrund.")

#Wieder den prozess stopen:
#ps aux | grep "connect-standalone.properties"
#und dann "kill pid"