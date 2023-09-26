import os
import subprocess
from datetime import datetime

def run_kafka_connector():
    # Überprüfen, ob das Verzeichnis ~/kafka/logs existiert
    log_directory = os.path.expanduser("~/kafka/logs")
    if not os.path.exists(log_directory):
        # Wenn nicht vorhanden, erstelle das Verzeichnis
        os.makedirs(log_directory)

    # Verwende das aktuelle Datum und die Uhrzeit, um den Logdateinamen zu erstellen
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = os.path.join(log_directory, f"connector_{current_datetime}.log")

    # Befehl zum Starten des Kafka-Connectors im Standalone-Modus und Ausgabe in die Logdatei
    command = f"/usr/local/kafka/bin/connect-standalone.sh /usr/local/kafka/config/connect-standalone.properties /usr/local/kafka/plugins/mongodb-sink.properties > {log_file_path} 2>&1 &"
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    print("Starte Kafka Connector im Hintergrund...")
    run_kafka_connector()
    print("Kafka Connector läuft im Hintergrund.")


#Wieder den prozess stopen:
#ps aux | grep "connect-standalone.properties"
#und dann "kill pid"