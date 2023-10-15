import os
import sys

from pydantic import ValidationError
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb')),
    os.path.join(os.path.dirname(__file__), '../helper'),
    os.path.join(os.path.dirname(__file__), '../core')
])

from typing import Dict, Any
from entry_exit_events_schema import EntryExitEvent, EntryExitEventValue
from base_processor import BaseProcessor




class DataProcessor(BaseProcessor):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)

    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message
        try:
            # print(f"Processing data: {data.raw_message}")
            entry_exit_event_value = self.validate_data(data)

            value = data.get('value')

            # entry_exit_event_value = EntryExitEventValue(**value)
            processed_message.add_data('value', entry_exit_event_value)


            entry_exit_events_datetime_obj = self._convert_to_datetime(data.get("timestamp"))
            self._write_data_for_patient_in_op_room(processed_message, entry_exit_events_datetime_obj, entry_exit_event_value)

        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise
    
    
    def _write_data_for_patient_in_op_room(self, processed_message, entry_exit_events_datetime_obj, entry_exit_event_value):
        for patient_id, timestamp_and_op_room in self.current_patients.items():
            op_room = timestamp_and_op_room.get("op_room")
            patient_entered_datetime_obj = timestamp_and_op_room.get("timestamp")
            print(f"op_room: {op_room}, patient_entered_datetime_obj: {patient_entered_datetime_obj}, entry_exit_events_datetime_obj: {entry_exit_events_datetime_obj}")
            if op_room == entry_exit_event_value.op_room and entry_exit_events_datetime_obj >= patient_entered_datetime_obj:
                schema = self._create_entry_exit_events_schema(entry_exit_events_datetime_obj, entry_exit_event_value, patient_id) 
                self.influxdb_connector.write_points([schema])
                processed_message.add_data("patient_id", patient_id)
                processed_message.add_data("op_room", op_room)


    def _create_entry_exit_events_schema(self, entry_exit_events_datetime_obj, entry_exit_event_value, patient_id):
        """Create a schema for the entry_exit_events measurement."""
        
        
        source = f"correlated_entry_exit_events"
        schema = {
            "measurement":  source,
            "tags": {
                "patient_id": patient_id,
                "person": entry_exit_event_value.person,
            },
            "time": f"{entry_exit_events_datetime_obj.isoformat()}Z",
            "fields": {
                "event": entry_exit_event_value.event,
            }
        }
        return schema

    

    def validate_data(self, data):
        """Validate data before writing to database """
        try:
            return EntryExitEvent(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise
