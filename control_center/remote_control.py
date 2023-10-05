import os
import signal
import sys
from time import sleep
import paramiko
import threading
import logging

# Adjust the path to include helper classes and functions
sys.path.append('../helper_classes_and_functions')
from config_loader import ConfigLoader
from background_script_runner import BackgroundScriptRunner


# Configure logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Constants
SCRIPTS_FIRST_PHASE = ["consume_op_team_info.py", "consume_op_record.py", "consume_patient_record.py"]
SCRIPTS_SECOND_PHASE = ["patient_data_generator.py"]
SCRIPTS_THIRD_PHASE = ["op_team.py", "pre_op_record.py"]
SCRIPTS_FOURTH_PHASE = ["entry_exit_event.py", "indoor_environment_data.py", "outdoor_environment.py"]
SCRIPTS_FIFTH_PHASE = ["patient_enter_event.py"]
SCRIPTS_SIXTH_PHASE = ["heart_rate.py", "blood_pressure.py", "bis.py", "etco2.py", "oxygen_saturation_producer.py", "staff_communication_during_op.py"]
SCRIPTS_POST_OP_PHASE = ["post_op_record.py"]
SCRIPTS_SEVENTH_PHASE = ["patient_exit_event.py"]
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

    def start_script_on_raspberry(self, script_path, is_cpp=False):
        """
        Start the given script on the Raspberry Pi.
        """
        try:
            self.connect()
            log_directory = f"/home/pi/op_data_generator/logs/"
            self.create_remote_directory_if_not_exist(log_directory)
            executable_name, log_path = self.prepare_script_execution(log_directory, script_path)
            if is_cpp:
                self.start_cpp_script(script_path, "server", log_path)
            else:
                self.start_python_script(script_path, executable_name, log_path)
        except Exception as e:
            logger.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: {e}")
        finally:
            self.disconnect()  

    def prepare_script_execution(self, log_directory, script_path):

        script_name = f"{os.path.basename(script_path)}"
        executable_name = os.path.splitext(script_name)[0]
        log_file_name = f"{executable_name}.log"
        log_path = os.path.join(log_directory, log_file_name)
        return executable_name, log_path
    
    def start_python_script(self, script_path, executable_name ,log_path):
        command = f'python {script_path} > {log_path} 2>&1 &'
        self.ssh.exec_command(command)
        self.log_script_start(script_path, executable_name)
        
    def start_cpp_script(self, script_path , executable_name, log_path):
        make_command = f"cd {script_path} && make"
        
        _, stdout, stderr = self.ssh.exec_command(make_command)
        make_output = stdout.read().decode().strip()
        make_error = stderr.read().decode().strip()
        
        if make_error:
            logger.error(f"Make command failed with error: {make_error}")
            return
        command = f'cd {script_path} && nohup ./{executable_name} > {log_path} 2>&1 &'  

        self.ssh.exec_command(command)
        
        command = f"ps aux | grep '{executable_name}' | grep -v grep | grep -v 'bash -c'"
        _, stdout, _ = self.ssh.exec_command(command)

        process_info = stdout.read().decode().strip()
        process_id = int(int(process_info.split()[1])) if process_info else None
        if process_id:
            self.process_ids.append(process_id)
            #self.started_scripts.append(generator_script_path)
            logger.info(f"Skript {executable_name} auf {self.pi_info['ip']} gestartet.")
        else:
            logger.error(f"Fehler beim Starten des Generators auf {self.pi_info['ip']}: Prozess nicht gefunden.")
        
    def log_script_start(self, script_path, script_name):
        process_id = self.get_process_id(script_path)
        if process_id:
            self.process_ids.append(process_id)
            logger.info(f"Started script {script_name} on {self.pi_info['ip']}.")
        else:
            logger.error(f"Failed to start the generator on {self.pi_info['ip']}: Process not found.")




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


def start_synchronization_server(raspberry_pis_config, executors):
    threads = []
    pi_name = "raspberry_pi_2"
    pi_info = raspberry_pis_config[pi_name]
    pi_info["pi_name"] = pi_name
    script_executor = ScriptExecutor(pi_info)
    script_path = f"op_data_generator/synchronization_server"
    thread = threading.Thread(target=script_executor.start_script_on_raspberry, args=(script_path, True))
    threads.append(thread)
    thread.start()
    executors.append(script_executor)

    # Wait for threads to finish
    wait_for_threads_to_finish(threads)

def wait_for_threads_to_finish(threads):
    for thread in threads:
        thread.join()


def execute_phase_scripts(phases, script_execution_config, raspberry_pis_config, script_paths_config, executors):
    for phase_scripts, prompt in phases:
        user_input = get_valid_input(prompt.format(phase_scripts), ['j', 'n'])
        if user_input == 'j':
            executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, phase_scripts)

def execute_remaining_scripts(all_scripts, script_execution_config, raspberry_pis_config, script_paths_config, executors):
    remaining_scripts = all_scripts - set(SCRIPTS_FIRST_PHASE) - set( SCRIPTS_SECOND_PHASE) - set( SCRIPTS_THIRD_PHASE) - set( SCRIPTS_POST_OP_PHASE)
    if remaining_scripts:
        user_input = get_valid_input("Möchten Sie den Restgeneratoren starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, list(remaining_scripts))


# Input validation
def get_valid_input(prompt, valid_choices):
    try:
        while True:
            user_input = input(prompt).lower() # type: ignore
            if user_input in valid_choices:
                return user_input
            else:
                logger.warning("Ungültige Eingabe. Bitte erneut versuchen.")
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt erkannt. Beende die Schleife.")
        raise


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
    wait_for_threads_to_finish(threads)
    return executers

def execute_scripts(config_loader):
    executors = []
    vital_parameter_executors = []
    local_runner = BackgroundScriptRunner()
    try:
        raspberry_pis_config = config_loader.load_config("raspberry_pis")
        script_execution_config = config_loader.load_config("script_execution")
        script_paths_config = config_loader.load_config("script_paths")
        ingestors_path_config = config_loader.load_config("ingestors_path")

        user_input = get_valid_input(f"Möchten Sie den Synchronisationsserver starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            start_synchronization_server(raspberry_pis_config, executors)

            user_input = get_valid_input(f"Möchten Sie den Synchronisationsclient starten? (j/n): ", ['j', 'n'])
            if user_input == 'j':
                start_synchronization_client(local_runner)

        phases = [
            (SCRIPTS_FIRST_PHASE, "Möchten Sie den {}-generator starten? (j/n): "),
            (SCRIPTS_SECOND_PHASE, "Möchten Sie den {}-generator starten? (j/n): "),
            (SCRIPTS_THIRD_PHASE, "Möchten Sie den {}-generator starten? (j/n): "),
            (SCRIPTS_FOURTH_PHASE, "Möchten Sie den {}-generator starten? (j/n): "),
            (SCRIPTS_FIFTH_PHASE, "Möchten Sie den {}-generator starten? (j/n): ")
        ]
        execute_phase_scripts(phases, script_execution_config, raspberry_pis_config, script_paths_config, executors)
        
        
        # all_scripts = get_all_scripts_from_config(script_execution_config)
        # execute_remaining_scripts(all_scripts, script_execution_config, raspberry_pis_config, script_paths_config, executors)
        
        
        user_input = get_valid_input("Möchten Sie die Ingestors starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            start_ingestors(local_runner, ingestors_path_config)

        user_input = get_valid_input("Möchten Sie die Patienten-Vitalparameter starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            vital_parameter_executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_SIXTH_PHASE)

        user_input = get_valid_input("Möchten Sie die Patienten-Vitalparameter beenden? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            for vital_parameter_executor in vital_parameter_executors:
                vital_parameter_executor.stop_generators_on_raspberry()

        
        user_input = get_valid_input("Möchten Sie den Post-OP-Generator starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_POST_OP_PHASE)

        user_input = get_valid_input("Möchten Sie die Patient_Exit_Event starten? (j/n): ", ['j', 'n'])
        if user_input == 'j':
            executors += execute_scripts_on_raspberries(script_execution_config, raspberry_pis_config, script_paths_config, SCRIPTS_SEVENTH_PHASE)


        return executors, local_runner
    except Exception as e:
        logger.error(f"Fehler beim Ausführen der Skripte: {e}")
        return executors, local_runner
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt in execute_scripts. Beende die Ausführung.")
        return executors, local_runner



def start_synchronization_client(local_runner):
    script_path = f"../synchronization_client"
    local_runner.run_cpp_program("synchronization", script_path, "client", "client.log")

def start_ingestors(local_runner, ingestors_path_config):
    for ingestor_name, ingestor_path in ingestors_path_config.items():
        script_path = f"../{ingestor_path}/{ingestor_name}"
        # ingestor_name without .py
        ingestor_name = os.path.splitext(ingestor_name)[0]
        print(f"============================: {ingestor_name}")
        local_runner.run_script(ingestor_name, script_path, f"{ingestor_name}.log")


if __name__ == "__main__":
    config_file = os.path.join( os.path.dirname(__file__) ,'config.json')
    executors = None
    local_runner = None
    try:        
        config_loader = ConfigLoader(config_file)
        executors, local_runner = execute_scripts(config_loader)
        input = input("Drücken Sie Enter, um die Generatoren zu beenden.")        
    except KeyboardInterrupt:
        logger.info("Skripte wurden vom Benutzer beendet.")
    except Exception as e:
        logger.error(f"Fehler beim Ausführen der Skripte: {e}")
    finally:
        if executors:
            for executer in executors:
                executer.stop_generators_on_raspberry()
                logger.info("Process IDs: %s", executer.process_ids)
        if local_runner:
            local_runner.stop_all_processes()
        logger.info("Skripte wurden beendet.")
        
        