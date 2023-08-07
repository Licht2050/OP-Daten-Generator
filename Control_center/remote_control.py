import time
import paramiko
import threading

def start_generator_on_raspberry_pi(ssh_client, generator_script):
    command = f"python3 {generator_script}"
    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
    return stdin, stdout, stderr

def stop_generator_on_raspberry_pi(ssh_client, process):
    process.send_signal(paramiko.Signal.SIGINT)
    process.close()

def start_generators_on_raspberry_pi(ssh_client, generator_scripts):
    for generator_script in generator_scripts:
        command = f"python3 {generator_script}"
        ssh_client.exec_command(command, get_pty=True)

def main():
    # Konfiguration der Raspberry Pis und ihrer Generatoren
    raspberry_pis = {
        "raspberry_pi_1": {
            "ip": "192.168.201.251",
            "generator_scripts": ["Patienten_Record.py", "Patientenvorerkrankungsakte.py", "Patientenurlaubsakte.py"]
        },
        "raspberry_pi_2": {
            "ip": "192.168.201.250",
            "generator_scripts": ["Heart_rate.py", "EtCO2.py", "BIS.py"]
        },
        "raspberry_pi_3": {
            "ip": "192.168.201.229",
            "generator_scripts": ["OP_RoomState.py"]
        },
        "raspberry_pi_4": {
            "ip": "192.168.201.167",
            "generator_scripts": ["OutdoorEnvironment_Generator.py"]
        }
    }

    try:
        # SSH-Verbindung zu jedem Raspberry Pi herstellen und Generatoren starten
        ssh_clients = {}
        generator_threads = []
        for pi_name, pi_config in raspberry_pis.items():
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(pi_config["ip"], username="pi", password="12345")
            ssh_clients[pi_name] = ssh_client

            generator_scripts = pi_config["generator_scripts"]
            generator_thread = threading.Thread(target=start_generators_on_raspberry_pi, args=(ssh_clients[pi_name], generator_scripts))
            generator_threads.append(generator_thread)
            generator_thread.start()

        # Warten, bis die Generatoren eine Weile laufen
        time.sleep(60)

        # Stoppen der Generatoren
        for pi_name, ssh_client in ssh_clients.items():
            ssh_client.exec_command("killall python3")

        # Warten, bis die Generatoren beendet sind
        for thread in generator_threads:
            thread.join()

        # Schließen der SSH-Verbindungen
        for ssh_client in ssh_clients.values():
            ssh_client.close()

    except Exception as e:
        print("Fehler:", e)

if __name__ == "__main__":
    main()
