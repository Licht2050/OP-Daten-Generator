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
from outdoor_environment_data_schema import OutdoorEnvironment, OutdoorEnvironmentValue
from base_processor import BaseProcessor



class DataProcessor(BaseProcessor):
    def __init__(self, influxdb_config: Dict[str, Any], patient_entry_exit_events_config: Dict[str, Any], mongodb_config, max_workers: int=10):
        super().__init__(influxdb_config, patient_entry_exit_events_config, mongodb_config, max_workers)

    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message
        value = data.get('value')
        try:
            self.validate_data(data)
            
            outdoor_environment_value = OutdoorEnvironmentValue(**value)
            processed_message.add_data('value', outdoor_environment_value)


            outdoor_data_datetiem_obj = self._convert_to_datetime(data.get("timestamp"))
            self._write_data_for_patient_in_op_room(outdoor_data_datetiem_obj, outdoor_environment_value)

        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise


    def _write_data_for_patient_in_op_room(self, outdoor_data_datetiem_obj,outdoor_environment_value):
        for patient_id, timestamp_and_op_room in self.current_patients.items():
            patient_entered_datetime_obj = timestamp_and_op_room.get("timestamp")

            if outdoor_data_datetiem_obj >= patient_entered_datetime_obj:
                schema = self.create_outdoor_environment_schema(outdoor_data_datetiem_obj, outdoor_environment_value, patient_id) 
                self.influxdb_connector.write_points([schema])
    
    def create_outdoor_environment_schema(self, outdoor_data_datetiem_obj, outdoor_environment_value, patient_id):
        """Create a schema for the outdoor_environment measurement."""
        source = f"correlated_outdoor_environment"
        # fields = {key: value for key, value in outdoor_environment_value.dict().items() if key not in ["external_temperature"]}
        fields = {key: value for key, value in outdoor_environment_value.dict().items()}
        schema = {
            "measurement":  source,
            "tags": {
                "patient_id": patient_id,
                "external_temperature": outdoor_environment_value.external_temperature,
            },
            "time": outdoor_data_datetiem_obj,
            "fields": fields
        }
        return schema


    
    def validate_data(self, data):
        """Validate data before writing to database """
        try:
            OutdoorEnvironment(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

