import json

class ConfigLoadError(Exception):
    pass

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None
    
    def load_config(self, source_name):
        try:
            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                self.config = config_data.get(source_name)
                if self.config:
                    print(self.config)
                if not self.config:
                    raise ConfigLoadError(f"source {source_name} configuration not found in config")
                return self.config
        except FileNotFoundError:
            raise ConfigLoadError("Config file not found")
        except json.JSONDecodeError as json_error:
            raise ConfigLoadError(f"Error decoding config file: {json_error}")
        except Exception as e:
            raise ConfigLoadError(f"Error loading config: {e}")
        
    def get_config(self):
        return self.config