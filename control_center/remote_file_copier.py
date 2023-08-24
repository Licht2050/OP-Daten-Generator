import os
import sys
import logging

# Adjust the path to include helper classes and functions
sys.path.append('../helper_classes_and_functions')
from config_loader import ConfigLoader
import paramiko

# Setting up the logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("remote_file_copier.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



class RemoteFileCopier:
    """Handles the task of connecting to a remote server, and copying files/folders."""
    
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport = None
        self.sftp = None

    def connect(self):
        """Establishes a connection to the remote server."""
        if not self.sftp:
            try:
                self.transport = paramiko.Transport((self.host, 22))
                self.transport.connect(username=self.username, password=self.password)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)
                logger.info(f"Connected to {self.host}")
            except (paramiko.AuthenticationException, paramiko.SSHException) as e:
                raise Exception(f"Error connecting to {self.host}: {e}")

    def disconnect(self):
        """Closes the connection to the remote server."""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        logger.info(f"Disconnected from {self.host}")
    
    def ensure_connected(self):
        """Ensures the connection is active, otherwise, re-establishes connection."""
        if not self.sftp:
            self.connect()
        
    def remote_directory_exists(self, remote_path):
        """Checks if a directory exists on the remote server."""
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False

    def create_remote_directory(self, remote_path):
        """Creates a directory on the remote server if it doesn't exist."""
        if not self.remote_directory_exists(remote_path): # Versuche, den Pfad zu überprüfen
            current_path = ""
            for component in remote_path.split("/"):
                if component:
                    current_path = os.path.join(current_path, component)
                    try:
                        self.sftp.stat(current_path)
                    except FileNotFoundError:
                        self.sftp.mkdir(current_path)
                        logger.info(f"Verzeichnis {current_path} auf {self.host} erstellt.")
        else:
            logger.info(f"Verzeichnis {remote_path} auf {self.host} existiert bereits.")
        

    def copy_file(self, local_path, remote_path):
        """Copies a single file to the remote server."""
        if not local_path.endswith(".pyc"):
            self.ensure_connected()
            self.sftp.put(local_path, remote_path)
            logger.info(f"Datei {local_path} nach {remote_path} auf {self.host} kopiert.")

    def copy_folder(self, local_folder, remote_folder):
        """Recursively copies a folder to the remote server."""
        self.ensure_connected()
        # Erstelle das Remote-Verzeichnis, wenn es nicht existiert
        self.create_remote_directory(remote_folder)

        for root, _, files in os.walk(local_folder):
            for file in files:
                if not file.endswith(".pyc"):
                    local_file_path = os.path.join(root, file)
                    remote_file_path = os.path.join(remote_folder, file)
                    self.sftp.put(local_file_path, remote_file_path)
                    logger.info(f"Datei {local_file_path} nach {remote_file_path} auf {self.host} kopiert.")

def copy_dependencies_to_remote(copier, base_dir, dependencies_config):
    """Copies the dependencies to the remote server."""   
    for dependency_name in dependencies_config:
        local_path = os.path.join(base_dir, dependency_name)
        remote_path = os.path.join("op_data_generator", dependency_name)
        copier.copy_folder(local_path, remote_path)
        logger.info(f"Finished copying {dependency_name} to {copier.host}")

def copy_scripts_to_remote(copier, base_dir, scripts_config, script_paths_config):
    """Copies the scripts to the remote server."""
    for script_name in scripts_config:
        local_path = os.path.join(base_dir, script_paths_config[script_name])
        remote_path = os.path.join("op_data_generator", script_paths_config[script_name])
        copier.copy_folder(local_path, remote_path)


def main():
    """Main execution function."""
    config_file = os.path.join( os.path.dirname(__file__) ,'config.json')
    config_loader = ConfigLoader(config_file)

    raspberry_pis_config = config_loader.load_config("raspberry_pis")
    script_execution_config = config_loader.load_config("script_execution")
    script_paths_config = config_loader.load_config("script_paths")
    dependency_paths_config = config_loader.load_config("dependency_paths")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    
    for pi_name, script_name in script_execution_config.items():
        pi_config = raspberry_pis_config[pi_name]
        remote_copier = RemoteFileCopier(
            pi_config.get("ip"),
            pi_config.get("username"),
            pi_config.get("password")
        )
        
        # Copying dependencies and scripts to the remote Raspberry Pi
        copy_dependencies_to_remote(remote_copier, base_dir, dependency_paths_config)
        copy_scripts_to_remote(remote_copier, base_dir, script_execution_config[pi_name], script_paths_config)
          
        remote_copier.disconnect()
        logger.info("="*50)



if __name__ == "__main__":
    main()