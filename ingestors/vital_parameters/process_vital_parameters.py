import json
import logging  
import os
import sys
import mmap
import struct
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
from paths_config import STATUS_HIGH, STATUS_LOW, STATUS_NORMAL, STATUS_UNKNOWN


class VitalsChecker:
    def __init__(self, thresholds_config):
        self.thresholds = thresholds_config
        self._setup_logging()
    def _setup_logging(self):
        """Initialize logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def check_vitals(self, processed_message):
        try:
            message = processed_message.raw_message
            message_dict = json.loads(message.value().decode('utf-8'))
            status = self.calculate_status(message_dict)
            processed_message.add_data('status', status)
            message_dict['status'] = status
            
        except json.JSONDecodeError:
            self.logger.error("JSON decoding failed")
        except KeyError as e:
            self.logger.error(f"Missing key in message: {e}")

    def calculate_status(self, message_dict):
        try:
            source = message_dict['source']
            value = message_dict['value']
            if source in self.thresholds:
                thresholds_for_source = self.thresholds[source]
                for key, limits in thresholds_for_source.items():
                    val = value.get(key)
                    if val is not None:
                        if val < limits[STATUS_LOW]:
                            return STATUS_LOW
                        elif val > limits[STATUS_HIGH]:
                            return STATUS_HIGH
                        else:
                            return STATUS_NORMAL
                    else:
                        return STATUS_UNKNOWN
        except json.JSONDecodeError:
            self.logger.error("JSON decoding failed")
        except KeyError as e:
            self.logger.error(f"Missing key in message: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")


# 
class SharedMemoryReader:
    def __init__(self, config_file):
        # Load the JSON configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.shared_memory_path = self.config['shared_memory_path']
        self.data_format = self.config['data_format']
        self.buffer_size = self.config['buffer_size']

        self.f = None
        self.mm = None

    def open(self):
        # Open the file and mmap
        self.f = open(self.shared_memory_path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), self.buffer_size, access=mmap.ACCESS_READ)

    def read_data(self):
        if self.mm is None:
            raise RuntimeError("Shared memory not opened. Call open() first.")
        
        # Reset position to beginning
        self.mm.seek(0)

        # Unpack the data based on the format defined in the config
        data_tuple = struct.unpack(self.data_format, self.mm.read(self.buffer_size))
        
        return data_tuple

    def close(self):
        if self.mm:
            self.mm.close()
        if self.f:
            self.f.close()

        self.mm = None
        self.f = None

if __name__ == "__main__":
    reader = SharedMemoryReader("config.json")
    
    try:
        reader.open()
        while True:
            data = reader.read_data()
            print("Message Duration:", data[0])
            print("Offset:", data[1])
            sleep(1)
    except KeyboardInterrupt:
        print("Stopping reader.")
    finally:
        reader.close()
