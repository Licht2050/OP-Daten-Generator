import os
import json
import sys
import logging
sys.path.append('../help_classes_and_functions')
from config_loader import ConfigLoader
import paramiko


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("remote_file_copier.log"),
        logging.StreamHandler()
    ]
)


class RemoteFileCopier:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport = None

    def connect(self):
        try:
            self.transport = paramiko.Transport((self.host, 22))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logging.info(f"Connected to {self.host}")
        except paramiko.AuthenticationException as e:
            raise Exception(f"Authentication failed for {self.host}: {e}")
        except paramiko.SSHException as e:
            raise Exception(f"SSH connection error to {self.host}: {e}")

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        logging.info(f"Disconnected from {self.host}")

    def create_remote_directory(self, remote_path):
        try:
            self.sftp.stat(remote_path)  # Versuche, den Pfad zu überprüfen
        except FileNotFoundError:  # Wenn stat einen Fehler wirft, existiert das Verzeichnis nicht
            current_path = ""
            for component in remote_path.split("/"):
                if component:
                    current_path = os.path.join(current_path, component)
                    try:
                        self.sftp.stat(current_path)
                    except FileNotFoundError:
                        self.sftp.mkdir(current_path)
                        logging.info(f"Verzeichnis {current_path} auf {self.host} erstellt.")
        else:
            logging.info(f"Verzeichnis {remote_path} auf {self.host} existiert bereits.")

    def copy_file(self, local_path, remote_path):
        self.sftp.put(local_path, remote_path)
        logging.info(f"Datei {local_path} nach {remote_path} auf {self.host} kopiert.")

    def copy_folder(self, local_folder, remote_folder):
        # Erstelle das Remote-Verzeichnis, wenn es nicht existiert
        self.create_remote_directory(remote_folder)

        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                remote_file_path = os.path.join(remote_folder, file)
                self.sftp.put(local_file_path, remote_file_path)
                logging.info(f"Datei {local_file_path} nach {remote_file_path} auf {self.host} kopiert.")


if __name__ == "__main__":
    config_file = os.path.join( os.path.dirname(__file__) ,'config.json')
    config_loader = ConfigLoader(config_file)

    raspberry_pis_config = config_loader.load_config("raspberry_pis")
    script_execution_config = config_loader.load_config("script_execution")
    script_paths_config = config_loader.load_config("script_paths")
    dependency_paths_config = config_loader.load_config("dependency_paths")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    

    for pi_name, script_name in script_execution_config.items():
        remote_copier = RemoteFileCopier(
            raspberry_pis_config[pi_name].get("ip"),
            raspberry_pis_config[pi_name].get("username"),
            raspberry_pis_config[pi_name].get("password")
        )
        remote_copier.connect()
        
        logging.info(f"Copying dependency files to {pi_name} ({remote_copier.host})")
        for dependency_name in dependency_paths_config:
            local_script_path = os.path.join(base_dir, dependency_name)
            remote_script_path = "op_data_generator/" + dependency_name
            remote_copier.copy_folder(local_script_path, remote_script_path)
            logging.info(f"Finished copying {dependency_name} to {pi_name} ({remote_copier.host})")

        logging.info(f"Copying files to {pi_name} ({remote_copier.host})")
        for script_name in script_execution_config[pi_name]:
            local_script_path = os.path.join(base_dir, script_paths_config[script_name])
            remote_script_path = "op_data_generator/" + script_paths_config[script_name]

            logging.info(f"Copying {script_name} to {pi_name} ({remote_copier.host})")
            # Kopiere das Skript-Verzeichnis in das Remote-Verzeichnis
            remote_copier.copy_folder(local_script_path, remote_script_path)

            logging.info(f"Finished copying {script_name} to {pi_name} ({remote_copier.host})")
        
        remote_copier.disconnect()
        logging.info("="*50)