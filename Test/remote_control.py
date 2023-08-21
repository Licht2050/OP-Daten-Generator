import os
import paramiko
import threading
import time

raspberry_pis = {
    "raspberry_pi_1": {
        "ip": "192.168.201.251",
        "generator_scripts": ["patient_data_generator.py", "op_team.py", "entry_exit_event.py"],
        "processes": []
    },
    "raspberry_pi_2": {
        "ip": "192.168.201.250",
        "generator_scripts": ["heart_rate.py", "blood_pressure.py", "op_room_state.py"],
        "processes": []
    },
    "raspberry_pi_3": {
        "ip": "192.168.201.229",
        "generator_scripts": ["bis.py", "outdoor_environment.py", "oxygen_saturation_producer.py"],
        "processes": []
    },
    "raspberry_pi_4": {
        "ip": "192.168.201.167",
        "generator_scripts": ["etco2.py", "staff_communication_during_op.py"],
        "processes": []
    }
}

started_scripts = []

def start_generator_on_raspberry(pi_info, generator_script_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Verbinden zum Raspberry Pi
        ssh.connect(pi_info["ip"], username='pi', password='12345')
        
        # Starten des Generators auf dem Raspberry Pi
        command = f'python {generator_script_path}'
        ssh.exec_command(command)

        # Prozess-ID des gestarteten Skripts erhalten und speichern
        stdin, stdout, stderr = ssh.exec_command(f"ps aux | grep 'python {generator_script_path}' | grep -v grep")
        process_info = stdout.read().decode().strip()
        print("----------------------------------------------------------------: Process info: " + process_info)
        if process_info:
            print(process_info)
            process_id = int(process_info.split()[1])  # Die zweite Spalte enthält die Prozess-ID
            pi_info["processes"].append(process_id)
        else:
            print(f"Fehler beim Starten des Generators auf {pi_info['ip']}: Prozess nicht gefunden.")
    except Exception as e:
        print(f"Fehler beim Starten des Generators auf {pi_info['ip']}: {e}")
    finally:
        # Schließen der SSH-Verbindung
        ssh.close()


def stop_generators_on_raspberry(pi_info):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(pi_info["ip"], username='pi', password='12345')
        
        for process_id in pi_info["processes"]:
            ssh.exec_command(f'kill {process_id}')
    except Exception as e:
        print(f"Fehler beim Beenden der Generatoren auf {pi_info['ip']}: {e}")
    finally:
        ssh.close()

def stop_generators():
    threads = []
    
    for pi_info in raspberry_pis.values():
        thread = threading.Thread(target=stop_generators_on_raspberry, args=(pi_info,))
        threads.append(thread)
        thread.start()

    # Warten auf das Ende der Threads
    for thread in threads:
        thread.join()



def main():
    generator_dir = os.path.dirname(os.path.abspath(__file__))
    threads = []

    # Starte "patienten_record_main.py", "entry_exit_event.py" und "staff_communication_during_op.py"
    pi_info = raspberry_pis["raspberry_pi_1"]
    for generator_script in ["entry_exit_event.py"]:
        print(generator_script)
        generator_script_path = f"op_data_generator/entry_exit_event    /{generator_script}"
        thread = threading.Thread(target=start_generator_on_raspberry, args=(pi_info, generator_script_path))
        threads.append(thread)
        thread.start()
        started_scripts.append(generator_script)
    
    # pi_info = raspberry_pis["raspberry_pi_4"]
    # generator_script = "staff_communication_during_op.py"
    # generator_script_path = f"/home/pi/{generator_script}"
    # thread = threading.Thread(target=start_generator_on_raspberry, args=(pi_info, generator_script_path))
    # threads.append(thread)
    # thread.start()
    # started_scripts.append(generator_script)
    

    # # Warten auf das Ende der Threads
    for thread in threads:
        thread.join()

    # print("Gestartete Skripte:", started_scripts)
    
    # # Benutzerabfrage für "op_team.py"
    # choice_op_team = input("Möchten Sie den 'op_team.py' Generator starten? (ja/nein): ")
    # if choice_op_team.lower() == "ja":
    #     pi_info = raspberry_pis["raspberry_pi_1"]
    #     generator_script = "op_team.py"
    #     generator_script_path = f"/home/pi/{generator_script}"
    #     start_generator_on_raspberry(pi_info, generator_script_path)
    #     started_scripts.append(generator_script)
        
    #     # Benutzerabfrage für die restlichen Skripte auf "raspberry_pi_1"
    #     choice_rest = input("Möchten Sie die restlichen Generatoren starten? (ja/nein): ")
    #     if choice_rest.lower() == "ja":
    #         pi_info = raspberry_pis["raspberry_pi_1"]
    #         for generator_script in pi_info["generator_scripts"]:
    #             if generator_script not in started_scripts and generator_script != "op_team.py":
    #                 generator_script_path = os.path.join(generator_dir, generator_script)
    #                 thread = threading.Thread(target=start_generator_on_raspberry, args=(pi_info, generator_script_path))
    #                 threads.append(thread)
    #                 thread.start()
    #                 started_scripts.append(generator_script)

    #         # Warten auf das Ende der Threads
    #         for thread in threads:
    #             thread.join()

    #         print("Restliche Generatoren auf raspberry_pi_1 wurden gestartet.")

    # Benutzerabfrage für das Stoppen der Generatoren
    choice_stop = input("Möchten Sie die Generatoren stoppen? (ja/nein): ")
    if choice_stop.lower() == "ja":
        stop_generators()

if __name__ == "__main__":
    main()
