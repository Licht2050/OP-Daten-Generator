import os
import sys
from typing import Any, Dict
from base import Base
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))

from paths_config import CONFIG_FILE_PATH
from config_loader import ConfigLoader
from kafka_consumer import KafkaTopicConsumer
from concurrent.futures import ThreadPoolExecutor




class PatientDataHandler(Base):
    def __init__(self, patient_data_config: Dict[str, Any], mongodb_config: Dict[str, Any], max_workers: int=10) -> None:
        super().__init__()







if __name__ == "__main__":
    # Load the configuration
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.get_all_configs()
    patient_data_config = config['topics']['patient_data']
    mangodb_config = config['mongodb']
    max_workers = config.get("threads", {}).get("max_workers", 10)


    # Start the staff communication handler
    patient_data_handler = PatientDataHandler(patient_data_config, max_workers=max_workers)