import os
import sys
import time
import paramiko
import threading
sys.path.append('../help_classes_and_functions')
from config_loader import ConfigLoader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')





class ScriptExecutor:
    def __init__(self):
        self.started_scripts = []
        self.process_ids = []
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.ssh.connect(self.pi_info["ip"], username=self.pi_info["username"], password=self.pi_info["password"])
            logging.info(f"Connected to {self.pi_info['ip']}")
        except paramiko.AuthenticationException as e:
            raise Exception(f"Authentication failed for {self.pi_info['ip']}: {e}")
        except paramiko.SSHException as e:
            raise Exception(f"SSH connection error to {self.pi_info['ip']}: {e}")
        
    def disconnect(self):
        self.ssh.close()
        logging.info(f"Disconnected from {self.pi_info['ip']}")

    def start_script_on_raspberry(self, pi_info, generator_script_path):
        try:
            self.pi_info = pi_info
            self.connect()
            
            log_file_name = generator_script_path.replace("/", "_").replace(".", "_") + ".log"
            log_path = os.path.join("logs", log_file_name)

            if not os.path.exists("logs"):
                os.makedirs("logs")

            # print("Python Path:", sys.path)
            # print("Current Working Directory:", os.getcwd())
            # Starten des Generators auf dem Raspberry Pi
            command = f'python {generator_script_path}'
            # self.ssh.exec_command(command)

            # stdin, stdout, stderr = self.ssh.exec_command(f"ps aux | grep 'python {generator_script_path}' | grep -v grep")
            # process_info = stdout.read().decode().strip()
            # if process_info:
            #     print(process_info)
            #     process_id = int(process_info.split()[1])  # Die zweite Spalte enthält die Prozess-ID
            #     self.process_ids.append(process_id)
            #     self.started_scripts.append(generator_script_path)
            # else:
            #     print(f"Fehler beim Starten des Generators auf {pi_info['ip']}: Prozess nicht gefunden.")


            stdin, stdout, stderr = self.ssh.exec_command(command)

            command_output = stdout.read().decode()  # Erfasse die Ausgabe des Skripts
            command_error = stderr.read().decode()    # Erfasse die Fehlerausgabe des Skripts
            if command_error:
                logging.error(f"Fehler beim Starten des Skripts {generator_script_path} auf {self.pi_info['ip']}: {command_error}")
                with open(log_path, "w") as log_file:
                    log_file.write(command_error)
            else:
                
                logging.info(f"Skript {generator_script_path} auf {self.pi_info['ip']} gestartet. Ausgabe: {command_output}")
                with open(log_path, "w") as log_file:
                    log_file.write(command_output)
                # Speichere die Prozess-ID des gestarteten Skripts
                # stdin, stdout, stderr = self.ssh.exec_command(f"pgrep -f 'python {generator_script_path}'")
                # process_id = int(stdout.read().decode().strip())
                # self.process_ids.append(process_id)
                # self.started_scripts.append(generator_script_path)
                # logging.info(f"Skript {generator_script_path} auf {self.pi_info['ip']} gestartet. Prozess-ID: {process_id}")
            
            # Prozess-ID des gestarteten Skripts erhalten und speichern
                stdin, stdout, stderr = self.ssh.exec_command(f"ps aux | grep 'python {generator_script_path}' | grep -v grep")
                process_info = stdout.read().decode().strip()
                print("-----------------------------------: " +process_info)
                if process_info:
                    
                    process_id = int(process_info.split()[1])  # Die zweite Spalte enthält die Prozess-ID
                    self.process_ids.append(process_id)
                    self.started_scripts.append(generator_script_path)
                    logging.info(f"Skript {generator_script_path} auf {self.pi_info['ip']} gestartet.")
                else:
                    logging.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: Prozess nicht gefunden.")
        except Exception as e:
            logging.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: {e}")
        finally:
            self.disconnect()

    def start_generators(self, script_paths):
        generator_dir = os.path.dirname(os.path.abspath(__file__))
        threads = []

        for script_path in script_paths:
            thread = threading.Thread(target=self.start_script_on_raspberry, args=(script_path,))
            threads.append(thread)
            thread.start()

        # Warten auf das Ende der Threads
        for thread in threads:
            thread.join()

    def stop_generators_on_raspberry(self):
        try:
            self.connect()
            
            for process_id in self.process_ids:
                self.ssh.exec_command(f'kill {process_id}')
        except Exception as e:
            print(f"Fehler beim Beenden der Generatoren auf {self.pi_info['ip']}: {e}")
        finally:
            self.disconnect()

    def stop_generators(self):
        threads = []
    
        thread = threading.Thread(target=self.stop_generators_on_raspberry)
        threads.append(thread)
        thread.start()

        # Warten auf das Ende des Threads
        for thread in threads:
            thread.join()

if __name__ == "__main__":

    config_file = os.path.join( os.path.dirname(__file__) ,'config.json')
    config_loader = ConfigLoader(config_file)

    raspberry_pis_config = config_loader.load_config("raspberry_pis")
    script_execution_config = config_loader.load_config("script_execution")
    script_paths_config = config_loader.load_config("script_paths")
    dependency_paths_config = config_loader.load_config("dependency_paths")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

    list_of_scripts_to_execute_first = ["patient_data_generator.py", "staff_communication_during_op.py", "entry_exit_event.py"]
    list_of_scripts_to_execute_second = ["op_team.py"]

    list_of_executer = []
    threads = []
    for pi_name, script_names in script_execution_config.items():
        for script_name in script_names:
            if script_name in list_of_scripts_to_execute_first:
                print("============================================================================: executing script: ", script_name)
                pi_info = raspberry_pis_config[pi_name]
                pi_info["pi_name"] = pi_name
                script_executor = ScriptExecutor(
                    
                )


                # remote_script_paths = ["op_data_generator/" + script_paths_config[script_name] + "/" + script_name for script_name in script_names]
                # script_executor.start_generators(remote_script_paths)
                script_path = f"op_data_generator/{script_paths_config[script_name]}/{script_name}"
                thread = threading.Thread(target=script_executor.start_script_on_raspberry, args=(pi_info, script_path,))
                threads.append(thread)
                thread.start()

                list_of_executer.append(script_executor)

    
    # Warten auf das Ende der Threads
    for thread in threads:
        thread.join()

    input = input("Press Enter to stop generators...")
    
    # print("Gestartete Skripte:")

    for executer in list_of_executer:
        executer.stop_generators_on_raspberry()
        print("process id: ", executer.process_ids)