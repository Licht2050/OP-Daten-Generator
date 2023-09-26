import datetime
import json
import os
import sys
from time import sleep
from typing import Any, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from base import Base
from config_loader import ConfigLoader
from shared_memory_reader import SharedMemoryReader
from paths_config import MICROSECONDS_IN_A_SECOND, STATUS_HIGH, STATUS_LOW, STATUS_NORMAL, STATUS_UNKNOWN


class VitalsChecker(Base):
    def __init__(self, thresholds_config: Dict[str, Any]):
        super().__init__()
        self.thresholds = thresholds_config
        self._setup_logging()

    def check_vitals(self, processed_message: Any)-> None:
        try:
            message_dict = self._decode_message(processed_message.raw_message)
            status = self.calculate_status(message_dict)
            processed_message.add_data('status', status)
            # message_dict['status'] = status
        except (json.JSONDecodeError, KeyError) as e:
            self._handle_exception(e)

    def calculate_status(self, message_dict: Dict[str, Any]) -> str:
        try:
            source = message_dict['source']
            value_dict = message_dict['value']
            if source in self.thresholds:
                return self._get_status_for_source(source, value_dict)
            else:
                return STATUS_UNKNOWN
        except KeyError as e:
            self._handle_exception(e)
            return STATUS_UNKNOWN

    def _get_status_for_source(self, source: str, value_dict: Dict[str, Any]) -> str:
        """Get the status for a specific source."""
        metric_thresholds = self.thresholds[source]
        if all(isinstance(v, dict) for v in metric_thresholds.values()):
            return self._get_complex_status(metric_thresholds, value_dict)
        else:
            return self._get_simple_status(metric_thresholds, value_dict[source])

    def _get_complex_status(self, metric_thresholds: Dict[str, Any], value_dict: Dict[str, Any]) -> str:
        """Get status for metrics with multiple components."""
        for component, value in value_dict.items():
            if component in metric_thresholds:
                component_thresholds = metric_thresholds[component]
                return self._get_status_based_on_value(value, component_thresholds)
        return STATUS_UNKNOWN
    
    def _get_simple_status(self, metric_thresholds: Dict[str, Any], value: Any)  -> str:
        """Get status for metrics with a single component."""
        return self._get_status_based_on_value(value, metric_thresholds)

    def _get_status_based_on_value(self, value: Any, thresholds: Dict[str, Any]) -> str:
        """Determine the status based on the value and thresholds."""
        if value < thresholds[STATUS_LOW]:
            return STATUS_LOW
        elif value > thresholds[STATUS_HIGH]:
            return STATUS_HIGH
        else:
            return STATUS_NORMAL
        
    

class TimSynchronization(Base):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config: Dict[str, Any] = config
        self._setup_logging()
        self.reader = SharedMemoryReader(self.config)
        self.reader.open()

    def synchronize(self, processed_message: Any)-> None:
        try:
            message_dict = self._decode_message(processed_message.raw_message)
            source = message_dict['source']
            if source in self.config['generators']:
                data = self.reader.read_data()
                if data:
                    estimate_send_time = self._calculate_estimate_time(message_dict['timestamp'], data[1], data[0])
                    processed_message.add_data('estimated_time', estimate_send_time)
                    message_dict['estimated_time'] = estimate_send_time
        except (json.JSONDecodeError, KeyError, Exception) as e:
            self._handle_exception(e)

    def _calculate_estimate_time(self, timestamp: str, offset: int, duration: int) -> str:
        time_in_microseconds = self._convert_to_microseconds(timestamp)
        # Calculate the estimated send time in microseconds        
        estimate_send_time = time_in_microseconds - offset
        return self._convert_from_microseconds(estimate_send_time)

    def _convert_to_microseconds(self, timestamp: str) -> int:
        time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').timestamp()
        return int(time * MICROSECONDS_IN_A_SECOND)
    
    def _convert_from_microseconds(self, time_in_microseconds: int) -> str:
        time_in_seconds = time_in_microseconds / MICROSECONDS_IN_A_SECOND
        estimate_send_datetime = datetime.datetime.fromtimestamp(time_in_seconds)
        return estimate_send_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    def close(self) -> None:
        self.reader.close()
    

if __name__ == "__main__":
    config_loader = ConfigLoader("../config/config.json")
    config = config_loader.load_config("synchronization")
    reader = SharedMemoryReader(config)
    
    try:
        reader.open()
        while True:
            data = reader.read_data()
            if data:
                print(f"Message Duration: {data[0]}, Offset: {data[1]}")
            sleep(1)
    except KeyboardInterrupt:
        print("Stopping reader.")
    finally:
        reader.close()
