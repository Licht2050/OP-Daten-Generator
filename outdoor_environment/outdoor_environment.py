import os
import random
import sys


# sys.path.append('../help_classes_and_functions')
sys.path.append(os.path.join(os.path.dirname(__file__), '../help_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

class OutdoorEnvironmentGenerator:
    
    def generate_outdoor_environment_info(self):
        temperature = round(random.uniform(-10.0, 40.0), 2)
        humidity = round(random.uniform(30.0, 80.0), 2)
        pressure = round(random.uniform(980.0, 1050.0), 2)
        wind_speed = round(random.uniform(0.0, 30.0), 2)

        outdoor_environment = {
            "Außentemperatur": temperature,
            "Luftfeuchtigkeit": humidity,
            "Luftdruck": pressure,
            "Windgeschwindigkeit": wind_speed,
        }

        return outdoor_environment
    

if __name__ == "__main__":

    source_name = "outdoor_environment"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    outdoor_environment_config = config_loader.load_config(source_name)

    sender = SourceDataSender(outdoor_environment_config)
    generator = OutdoorEnvironmentGenerator()

    try:
        print("Umweltparameter-Generator für draußen gestartet:")
        sender.send_continuous_data(source_name, lambda: generator.generate_outdoor_environment_info())
    except Exception as e:
        print("Error: {e}")
    finally:
        sender.disconnect_producer()