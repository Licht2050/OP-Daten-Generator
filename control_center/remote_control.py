import os
import sys
import time
import paramiko
import threading
sys.path.append('../help_classes_and_functions')
from config_loader import ConfigLoader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)




class ScriptExecutor:
    def __init__(self, pi_info):
        self.pi_info = pi_info
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

    def create_remote_directory(self, directory):
        command = f"mkdir -p {directory}"
        stdin, stdout, stderr = self.ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            logger.info(f"Created remote directory: {directory}")
        else:
            logger.error(f"Failed to create remote directory: {directory} - Error: {stderr.read().decode().strip()}")

    def get_process_id(self, generator_script_path):
        # command = f"pgrep -f 'python {generator_script_path}'"
        command = f"ps aux | grep 'python {generator_script_path}' | grep -v grep"
        stdin, stdout, stderr = self.ssh.exec_command(command)

        process_info = stdout.read().decode().strip()
        return int(int(process_info.split()[1])) if process_info else None

    def start_script_on_raspberry(self, generator_script_path):
        try:
            self.connect()
            
            script_name = f"{os.path.basename(generator_script_path)}"
            script_name_without_extension = os.path.splitext(script_name)[0]
            remote_log_directory = f"/home/pi/op_data_generator/logs/"
            

            

            self.create_remote_directory_if_not_exist(remote_log_directory)

            log_file_name = f"{script_name_without_extension}.log"
            log_path = os.path.join(remote_log_directory, log_file_name)

                    
            command = f'python {generator_script_path} > {log_path} 2>&1 &'
            self.ssh.exec_command(command)

            # Prozess-ID des gestarteten Skripts erhalten und speichern
            
            process_id = self.get_process_id(generator_script_path)
            if process_id:
                print(process_id)
                self.process_ids.append(process_id)
                #self.started_scripts.append(generator_script_path)
                logging.info(f"Skript {script_name} auf {self.pi_info['ip']} gestartet.")
            else:
                logging.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: Prozess nicht gefunden.")
        except Exception as e:
            logging.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: {e}")
        finally:
            self.disconnect()

    def create_remote_directory_if_not_exist(self, remote_log_directory):
        command = f"if [ -d '{remote_log_directory}' ]; then echo 'existiert'; else echo 'existiert nicht'; fi"
        stdin, stdout, stderr = self.ssh.exec_command(command)

            # Den Befehlsergebnis lesen
        path_status = stdout.read().decode().strip()

        if path_status == "existiert":
            logging.info(f"Pfad {remote_log_directory} existiert bereits.")
        else:
                # Befehl ausführen, um den Pfad zu erstellen
            create_command = f"mkdir -p {remote_log_directory}"
            stdin, stdout, stderr = self.ssh.exec_command(create_command)
                
                # Warten, bis der Befehl abgeschlossen ist
            exit_status = stdout.channel.recv_exit_status()
                
            if exit_status == 0:
                logging.info(f"Pfad {remote_log_directory} erstellt.")
            else:
                logging.error(f"Fehler beim Erstellen des Pfads {remote_log_directory} auf {self.pi_info['ip']}: {stderr.read().decode().strip()}")

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
                logger.info(f"Executing script: {script_name}")
                pi_info = raspberry_pis_config[pi_name]
                pi_info["pi_name"] = pi_name
                script_executor = ScriptExecutor(
                    pi_info
                )


                # remote_script_paths = ["op_data_generator/" + script_paths_config[script_name] + "/" + script_name for script_name in script_names]
                # script_executor.start_generators(remote_script_paths)
                script_path = f"op_data_generator/{script_paths_config[script_name]}/{script_name}"
                thread = threading.Thread(target=script_executor.start_script_on_raspberry, args=(script_path,))
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
        logger.info("Process IDs: %s", executer.process_ids)