import logging
import os
import random
import sys


# Adjust the path to include helper classes and functions
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper_classes_and_functions'))
from config import CONFIG_FILE_PATH, OUTDOOR_SOURCE_NAME, OUTDOOR_TEMP_RANGE, OUTDOOR_HUMIDITY_RANGE, OUTDOOR_PRESSURE_RANGE, OUTDOOR_WIND_SPEED_RANGE
from config_loader import ConfigLoader
from source_data_sender import SourceDataSender

# Set up basic logging for the script
logging.basicConfig(level=logging.INFO)

class OutdoorEnvironmentGenerator:
    """
    This class is responsible for generating random outdoor environment parameters.
    """



    def generate_outdoor_environment_info(self):
        """
        Generate a dictionary containing random values for outdoor environmental factors.
        
        Returns:
            dict: Contains parameters like temperature, humidity, pressure, and wind speed.
        """
        outdoor_environment = {
            "Außentemperatur": round(random.uniform(*OUTDOOR_TEMP_RANGE), 2),
            "Luftfeuchtigkeit": round(random.uniform(*OUTDOOR_HUMIDITY_RANGE), 2),
            "Luftdruck": round(random.uniform(*OUTDOOR_PRESSURE_RANGE), 2),
            "Windgeschwindigkeit": round(random.uniform(*OUTDOOR_WIND_SPEED_RANGE), 2),
        }
        return outdoor_environment

def main():
    """
    Main execution function. It sets up the environment generator and the Kafka sender,
    and then starts continuously sending the generated data.
    """
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    outdoor_environment_config = config_loader.load_config(OUTDOOR_SOURCE_NAME)

    # Initialize the Kafka sender and the environment data generator
    sender = SourceDataSender(outdoor_environment_config)
    generator = OutdoorEnvironmentGenerator()

    # Continuously generate and send data to Kafka
    try:
        logging.info("Umweltparameter-Generator für draußen gestartet:")
        sender.send_continuous_data(OUTDOOR_SOURCE_NAME, lambda: generator.generate_outdoor_environment_info())
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sender.disconnect_producer()     

if __name__ == "__main__":
    main()
    