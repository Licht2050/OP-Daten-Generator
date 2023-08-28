import os
import sys
import paramiko
import threading
import logging

# Adjust the path to include helper classes and functions
sys.path.append('../helper_classes_and_functions')
from config_loader import ConfigLoader


# Configure logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Constants
SCRIPTS_FIRST_PHASE = ["consume_op_team_info.py", "consume_op_record.py", "consume_patient_record.py"]
SCRIPTS_SECOND_PHASE = ["patient_data_generator.py"]
SCRIPTS_THIRD_PHASE = ["op_team.py", "pre_op_record.py"]
SCRIPTS_POST_OP_PHASE = ["post_op_record.py"]
# SCRIPTS_FIRST_PHASE = ["patient_data_generator.py", "staff_communication_during_op.py", "entry_exit_event.py"]
# SCRIPTS_SECOND_PHASE = ["op_team.py"]


class ScriptExecutor:
    """
    Class to execute and manage scripts on a Raspberry Pi.
    """
    def __init__(self, pi_info):
        """
        Initializes the ScriptExecutor.

        Args:
            pi_info (dict): A dictionary containing the information of the Raspberry Pi.
        """
        self.pi_info = pi_info
        self.process_ids = []
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        """
        Establish an SSH connection to the Raspberry Pi.
        """
        try:
            self.ssh.connect(self.pi_info["ip"], username=self.pi_info["username"], password=self.pi_info["password"])
            logger.info(f"Connected to {self.pi_info['ip']}")
        except paramiko.AuthenticationException as e:
            raise Exception(f"Authentication failed for {self.pi_info['ip']}: {e}")
        except paramiko.SSHException as e:
            raise Exception(f"SSH connection error to {self.pi_info['ip']}: {e}")
        
    def disconnect(self):
        """
        Close the SSH connection.
        """
        self.ssh.close()
        logging.info(f"Disconnected from {self.pi_info['ip']}")

    def ensure_remote_directory(self, directory):
        """
        Ensure the remote directory exists.
        """
        command = f"mkdir -p {directory}"
        _, _, stderr = self.ssh.exec_command(command)
        error = stderr.read().decode().strip()
        if error:
            logger.error(f"Failed to create remote directory: {directory} - Error: {error}")
        else:
            logger.info(f"Ensured remote directory: {directory}")


    def get_process_id(self, generator_script_path):
        """
        Get the process ID for the given script path.
        """
        # command = f"pgrep -f 'python {generator_script_path}'"
        command = f"ps aux | grep 'python {generator_script_path}' | grep -v grep"
        _, stdout, _ = self.ssh.exec_command(command)

        process_info = stdout.read().decode().strip()
        return int(int(process_info.split()[1])) if process_info else None

    def start_script_on_raspberry(self, generator_script_path):
        """
        Start the given script on the Raspberry Pi.
        """
        try:
            self.connect()
            
            remote_log_directory = f"/home/pi/op_data_generator/logs/"
            self.create_remote_directory_if_not_exist(remote_log_directory)

            script_name = f"{os.path.basename(generator_script_path)}"
            script_name_without_extension = os.path.splitext(script_name)[0]
            
            

            log_file_name = f"{script_name_without_extension}.log"
            log_path = os.path.join(remote_log_directory, log_file_name)

                    
            command = f'python {generator_script_path} > {log_path} 2>&1 &'
            self.ssh.exec_command(command)

            # Prozess-ID des gestarteten Skripts erhalten und speichern
            
            process_id = self.get_process_id(generator_script_path)
            if process_id:
                self.process_ids.append(process_id)
                #self.started_scripts.append(generator_script_path)
                logger.info(f"Skript {script_name} auf {self.pi_info['ip']} gestartet.")
            else:
                logger.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: Prozess nicht gefunden.")
        except Exception as e:
            logger.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: {e}")
        finally:
            self.disconnect()

    def create_remote_directory_if_not_exist(self, remote_log_directory):
        command = f"if [ -d '{remote_log_directory}' ]; then echo 'existiert'; else echo 'existiert nicht'; fi"
        stdin, stdout, stderr = self.ssh.exec_command(command)

            # Den Befehlsergebnis lesen
        path_status = stdout.read().decode().strip()

        if path_status == "existiert":
            logger.info(f"Pfad {remote_log_directory} existiert bereits.")
        else:
            # Befehl ausführen, um den Pfad zu erstellen
            self.ensure_remote_directory(remote_log_directory)


    def start_generators(self, script_paths):
        
        threads = [threading.Thread(target=self.start_script_on_raspberry, args=(script_path,)) for script_path in script_paths]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


    def stop_generators_on_raspberry(self):
        """
        Stop all scripts managed by this executor on the Raspberry Pi.
        """
        try:
            self.connect()
            
            for process_id in self.process_ids:
                self.ssh.exec_command(f'kill {process_id}')
        except Exception as e:
            logger.error(f"Fehler beim Beenden der Generatoren auf {self.pi_info['ip']}: {e}")
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



def get_all_scripts_from_config(script_execution_config):
    all_scripts = set()
    for script_names in script_execution_config.values():
        all_scripts.update(script_names)
    return all_scripts


def execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, list_of_scripts_to_execute):
    threads = []
    executers = []

    for pi_name, script_names in script_execution_config.items():
        for script_name in script_names:
            if script_name in list_of_scripts_to_execute:
                pi_info = raspberry_pis_config[pi_name]
                pi_info["pi_name"] = pi_name
                script_executor = ScriptExecutor(pi_info)
                script_path = f"op_data_generator/{script_paths_config[script_name]}/{script_name}"
                thread = threading.Thread(target=script_executor.start_script_on_raspberry, args=(script_path,))
                threads.append(thread)
                thread.start()
                executers.append(script_executor)
    
    # Wait for threads to finish
    for thread in threads:
        thread.join()

    return executers


def execute_scripts(config_loader):
    raspberry_pis_config = config_loader.load_config("raspberry_pis")
    script_execution_config = config_loader.load_config("script_execution")
    script_paths_config = config_loader.load_config("script_paths")

    # Execute first set of scripts
    executors = execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_FIRST_PHASE)

    # User input to decide if they want to start the rest of the generators
    if get_valid_input(f"Möchten Sie den {SCRIPTS_SECOND_PHASE}-generator starten? (j/n): ", ['j', 'n']) == 'j':
        executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_SECOND_PHASE)

        if get_valid_input(f"Möchten Sie den {SCRIPTS_THIRD_PHASE}-generator starten? (j/n): ", ['j', 'n']) == 'j':
            executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_THIRD_PHASE)
        
        if get_valid_input("Möchten Sie den Restgeneratoren starten? (j/n): ", ['j', 'n']) == 'j':
            # Execute the remaining scripts that are not in the first or second phase
            all_scripts = get_all_scripts_from_config(script_execution_config)
            remaining_scripts = all_scripts - set(SCRIPTS_FIRST_PHASE) - set(SCRIPTS_SECOND_PHASE) - set(SCRIPTS_THIRD_PHASE) - set(SCRIPTS_POST_OP_PHASE)
            if remaining_scripts:
                executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, list(remaining_scripts))
            
            if get_valid_input("Möchten Sie den Post-OP-Generator starten? (j/n): ", ['j', 'n']) == 'j':
                executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_POST_OP_PHASE)
    return executors


# Input validation
def get_valid_input(prompt, valid_choices):
    while True:
        user_input = input(prompt).lower() # type: ignore
        if user_input in valid_choices:
            return user_input
        else:
            logger.warning("Ungültige Eingabe. Bitte erneut versuchen.")



if __name__ == "__main__":

    config_file = os.path.join( os.path.dirname(__file__) ,'config.json')
    config_loader = ConfigLoader(config_file)
    executors = execute_scripts(config_loader)

    input = input("Drücken Sie Enter, um die Generatoren zu beenden.")
    

    for executer in executors:
        executer.stop_generators_on_raspberry()
        logger.info("Process IDs: %s", executer.process_ids)