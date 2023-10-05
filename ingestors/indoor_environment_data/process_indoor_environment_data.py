from datetime import datetime
import os
import sys
import threading
import json
from pydantic import ValidationError

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../config'),
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb')),
    os.path.join(os.path.dirname(__file__), '../helper'),
    os.path.join(os.path.dirname(__file__), '../db_connectors')
])


from typing import Dict, Any
from indoor_environment_data_schema import IndoorEnvironmentDataStatus, IndoorEnvironmentDataValue
from base_processor import BaseProcessor


class DataProcessor(BaseProcessor):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)


    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message     
        try:
            # print(f"Processing data: {data.raw_message}")
            self._validate_data(data)
            
            indoor_data_datetime_obj = self._convert_to_datetime(data.get("timestamp"))
            value = data.get('value')

            indoor_environment_value = IndoorEnvironmentDataValue(**value)
            processed_message.add_data('value', indoor_environment_value)

            if self.current_patients:
                for patient_id, timestamp_and_op_room in self.current_patients.items():
                    op_room = timestamp_and_op_room.get("op_room")
                    patient_entered_datetime_obj = self._convert_to_datetime(timestamp_and_op_room.get("timestamp"))

                    if op_room == indoor_environment_value.op_room and indoor_data_datetime_obj >= patient_entered_datetime_obj:
                        schema = self._create_indoor_environment_schema(processed_message.to_dict(), patient_id) 
                        self.influxdb_connector.write_points([schema])
        except ValidationError as e:
            self.logger.error(f"Error processing inddor environment data: {e}")
            raise
    
    def _create_indoor_environment_schema(self, processed_message, patient_id):
        timestamp_str = processed_message.get("timestamp")
        timestamp = self._convert_to_datetime(timestamp_str)

        value_data = processed_message.get("value", {})

        indoor_environment_value = value_data.model_dump(by_alias=False)
        source = patient_id + "_indoor_environment_data"
        fields = {key: value for key, value in indoor_environment_value.items() if key != "op_room" and key != "door_status"}

        schema = {
            "measurement": source,
            "tags": {
                "door_status": indoor_environment_value.get("door_status"),
            },
            "time": timestamp.isoformat() + "Z",
            "fields": fields

        }
        return schema

            

    def _validate_data(self, data):
        """Validate data before writing to database """
        try:
            IndoorEnvironmentDataStatus(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

