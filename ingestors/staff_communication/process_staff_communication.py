from datetime import datetime
import os
import sys
from typing import Any, Dict


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb')),
    os.path.join(os.path.dirname(__file__), '../helper'),
])

from base_processor import BaseProcessor

class DataProcessor(BaseProcessor):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)
        

    def process_data(self, msg):
        """Process data before writing to database """
        processed_data = msg.raw_message
        try:
            staff_communication_datetime_obj = self._convert_to_datetime(processed_data.get("timestamp"))
            value = processed_data.get('value')

            if self.current_patients:
                for patient_id, timestamp_and_op_room in self.current_patients.items():
                    op_room = timestamp_and_op_room.get("op_room")
                    patient_entered_datetime_obj = self._convert_to_datetime(timestamp_and_op_room.get("timestamp"))
                    
                    if op_room == value.get("op_room") and staff_communication_datetime_obj >= patient_entered_datetime_obj:
                        schema = self.create_staff_communication_schema(processed_data, patient_id)
                        self.influxdb_connector.write_points([schema])
        except Exception as e:
            self.logger.error(f"Error processing staff communication data: {e}")
            raise


    def create_staff_communication_schema(self, msg: Dict[str, Any], patient_id) -> Dict[str, Any]:
        """Create a schema for the staff_communication measurement.

        Args:
            data (dict): The staff communication data.

        Returns:
            dict: The InfluxDB schema.
        """
        timestamp_str = msg.get("timestamp")
        timestamp = self._convert_to_datetime(timestamp_str)
        value_data = msg.get("value", {})

        source = patient_id + "_staff_communication"
        schema = {
            "measurement":  source,
            "tags": {
                "sender": value_data.get("sender", "Unknown"),
            },
            "time": timestamp.isoformat() + "Z",
            "fields": {
                "message": value_data.get("message", ""),
            }
        }
        return schema
    

