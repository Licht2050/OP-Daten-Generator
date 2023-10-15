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
    os.path.join(os.path.dirname(__file__), '../core'),
    os.path.join(os.path.dirname(__file__), '../db_connectors')
])


from typing import Dict, Any
from indoor_environment_data_schema import IndoorEnvironmentDataStatus, IndoorEnvironmentDataValue
from base_processor import BaseProcessor


class DataProcessor(BaseProcessor):
    def __init__(self, influxdb_config: Dict[str, Any], 
                 patient_entry_exit_events_config: Dict[str, Any], 
                 mongodb_config, max_workers: int=10):
        super().__init__(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)
        

    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message     
        try:
            # print(f"Processing data: {data.raw_message}")
            self._validate_data(data)
            
           
            value = data.get('value')

            indoor_environment_value = IndoorEnvironmentDataValue(**value)
            processed_message.add_data('value', indoor_environment_value)

            indoor_data_datetime_obj = self._convert_to_datetime(data.get("timestamp"))
            self._write_data_for_patient_in_op_room(processed_message, indoor_data_datetime_obj, indoor_environment_value)
        except ValidationError as e:
            self.logger.error(f"Error processing inddor environment data: {e}")
            raise
    


    def _write_data_for_patient_in_op_room(self, processed_message, indoor_data_datetime_obj, indoor_environment_value):
        
        for patient_id, timestamp_and_op_room in self.current_patients.items():
            op_room = timestamp_and_op_room.get("op_room")
            patient_entered_datetime_obj = timestamp_and_op_room.get("timestamp")
            # print(f"patient_id: {patient_id}, op_room: {op_room}, indoor_environment_valu:{indoor_environment_value.op_room}  patient_entered_datetime_obj: {patient_entered_datetime_obj}, indoor_data_datetime_obj: {indoor_data_datetime_obj}")
            if op_room == indoor_environment_value.op_room and indoor_data_datetime_obj >= patient_entered_datetime_obj:
                schema = self._create_indoor_environment_schema( indoor_data_datetime_obj, indoor_environment_value, patient_id) 
                self.influxdb_connector.write_points([schema])
                processed_message.add_data("patient_id", patient_id)
                processed_message.add_data("op_room", op_room)
        return False
    
    
    def _create_indoor_environment_schema(self, indoor_data_datetime_obj, indoor_environment_value, patient_id):
        """Create a schema for the indoor_environment measurement."""
        source = f"correlated_indoor_environment_data"
        indoor_environment_value_dict = indoor_environment_value.model_dump()
        fields = {key: value for key, value in indoor_environment_value_dict.items() if key not in ["op_room", "door_state"]}

        schema = {
            "measurement": source,
            "tags": {
                "patient_id": patient_id,
                "door_status": indoor_environment_value.door_state,
            },
            "time": f"{indoor_data_datetime_obj.isoformat()}Z",
            "fields": fields

        }
        # print(f"Schema: {schema}")
        return schema

            

    def _validate_data(self, data):
        """Validate data before writing to database """
        try:
            IndoorEnvironmentDataStatus(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

