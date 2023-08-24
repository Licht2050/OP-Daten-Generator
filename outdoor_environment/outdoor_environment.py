import logging
import os
import random
import sys


# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

# Set up basic logging for the script
logging.basicConfig(level=logging.INFO)

class OutdoorEnvironmentGenerator:
    """
    This class is responsible for generating random outdoor environment parameters.
    """

    TEMP_RANGE = (-10.0, 40.0)
    HUMIDITY_RANGE = (30.0, 80.0)
    PRESSURE_RANGE = (980.0, 1050.0)
    WIND_SPEED_RANGE = (0.0, 30.0)

    def generate_outdoor_environment_info(self):
        """
        Generate a dictionary containing random values for outdoor environmental factors.
        
        Returns:
            dict: Contains parameters like temperature, humidity, pressure, and wind speed.
        """
        outdoor_environment = {
            "Außentemperatur": round(random.uniform(*self.TEMP_RANGE), 2),
            "Luftfeuchtigkeit": round(random.uniform(*self.HUMIDITY_RANGE), 2),
            "Luftdruck": round(random.uniform(*self.PRESSURE_RANGE), 2),
            "Windgeschwindigkeit": round(random.uniform(*self.WIND_SPEED_RANGE), 2),
        }
        return outdoor_environment

def main():
    """
    Main execution function. It sets up the environment generator and the Kafka sender,
    and then starts continuously sending the generated data.
    """
    source_name = "outdoor_environment"
    config_file_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    config_loader = ConfigLoader(config_file_path)
    outdoor_environment_config = config_loader.load_config(source_name)

    # Initialize the Kafka sender and the environment data generator
    sender = SourceDataSender(outdoor_environment_config)
    generator = OutdoorEnvironmentGenerator()

    # Continuously generate and send data to Kafka
    try:
        print("Umweltparameter-Generator für draußen gestartet:")
        sender.send_continuous_data(source_name, lambda: generator.generate_outdoor_environment_info())
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sender.disconnect_producer()     

if __name__ == "__main__":
    main()
    