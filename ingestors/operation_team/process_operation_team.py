import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/mongodb')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions')))

from pydantic import ValidationError
from typing import Dict, Any
from base import Base
from db_schema import OperationTeam


class DataProcessor(Base):
    class DataProcessingError(Exception):
        """Raised when there is an error during data processing."""
        pass

    def __init__(self):
        super().__init__()
        self._setup_logging()

    def process_data(self, processed_message) -> None:
        # print(f"Processing data: {processed_message.raw_message}")
        data = processed_message.raw_message
        source = data.get('source')
        value = data.get('value')
        patient_id = value.get('Patient_ID')
        
        if value is None or patient_id is None:
            self.logger.error(f"Failed to process data: No value or patient ID found")
            raise self.DataProcessingError("Missing value or patient ID")
        
        try:
            if source == 'op_team':
                self.process_op_team_data(value, processed_message)
            processed_message.add_data('patient_id', patient_id)
            
        except ValidationError as e:
            self.logger.error(f"Failed to validate data: {e}")
            raise self.DataProcessingError("Validation error")
        

    def process_op_team_data(self, value, processed_message):
        try:
            op_team = OperationTeam(**value)
            processed_message.add_data('value', op_team)

        except ValidationError as e:
            self._handle_exception(f"Error validating data: {e}")
            raise
            
