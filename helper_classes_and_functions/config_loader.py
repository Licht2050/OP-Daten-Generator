import json

class ConfigLoadError(Exception):
    """Exception raised for errors encountered during config loading."""
    pass

class ConfigLoader:
    """Loads the configuration from the config file."""
    def __init__(self, config_file):
        self.config_file = config_file
        self.all_configs = self._load_all_configs()
        self.config = None
    

    def _load_all_configs(self):
        """Load all configurations from the file."""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ConfigLoadError("Config file not found")
        except json.JSONDecodeError as json_error:
            raise ConfigLoadError(f"Error decoding config file: {json_error}")
        except Exception as e:
            raise ConfigLoadError(f"Error loading config: {e}")

    def load_config(self, source_name):
        """Load a specific configuration by source name."""
        self.config = self.all_configs.get(source_name)
        if not self.config:
            raise ConfigLoadError(f"source {source_name} configuration not found in config")
        return self.config
    
    def get_all_configs(self):
        """Retrieve all configurations."""
        return self.all_configs

    def get_current_config(self):    
        """Retrieve the currently loaded configuration."""
        return self.config