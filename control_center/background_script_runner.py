import subprocess
import os
import signal
from base import Base
from typing import Optional



class BackgroundScriptRunner(Base):
    def __init__(self):
        """Initialize a dictionary to store processes and set up logging."""
        super().__init__()
        self.processes = {}  # Store processes in a dictionary
        self._setup_logging()


    def run_script(self, script_name: str, script_path: str, log_path: str) -> None:
        """Run a Python script in the background.
        
        Args:
            script_name: The name to associate with the script.
            script_path: The path to the script.
            log_path: The path to store the log file.
        """
        abs_path = os.path.abspath(script_path)
        if not os.path.exists(abs_path):
            self._handle_exception(f"Script {abs_path} does not exist.")
            return

        with open(log_path, 'w') as log_file:
            process = subprocess.Popen(
                ["/usr/bin/python3", "-u", abs_path],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(abs_path) # Set the current working directory for the process
            )
            self.processes[script_name] = process
            self.logger.info(f"Started script {abs_path} with PID {process.pid}")

    def run_cpp_program(self, project_name: str, project_dir: str, executable_name: str, log_path: str) -> None:
        """Run a C++ program in the background after compiling it.
        
        Args:
            project_name: The name to associate with the project.
            project_dir: The directory where the project is located.
            executable_name: The name of the executable.
            log_path: The path to store the log file.
        """
        try:
            result = subprocess.run(
                ["make"],
                cwd=project_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.logger.info(f"Compilation output: {result.stdout.decode()}")

            executable_path = os.path.join(project_dir, executable_name)
            with open(log_path, 'w') as log_file:
                process = subprocess.Popen(
                    [executable_path],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    cwd=project_dir  # Set the current working directory for the process
                )
                self.processes[project_name] = process
                self.logger.info(f"Started C++ program {executable_name} with PID {process.pid}")
        except subprocess.CalledProcessError as e:
            self._handle_exception(f"Compilation failed: {e.stderr.decode()}")

    def get_process_id(self, name: str) -> Optional[int]:
        """Get the process ID associated with a name.
        
        Args:
            name: The name associated with the process.
        
        Returns:
            The process ID if the process exists, else None.
        """
        process = self.processes.get(name, None)
        if process:
            return process.pid
        else:
            return None

    def stop_process(self, name: str) -> None:
        """Stop a process given its name.
        
        Args:
            name: The name associated with the process.
        """
        process = self.processes.get(name, None)
        if process:
            os.kill(process.pid, signal.SIGTERM)
            self.logger.info(f"Stopped process {name} with PID {process.pid}")
            del self.processes[name]
        else:
            self.logger.warning(f"No process with the name {name} is currently running.")
    
    def stop_all_processes(self) -> None:
        """Stop all running processes."""
        for name in list(self.processes.keys()):
            self.stop_process(name)
