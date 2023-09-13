import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/mongodb')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions')))

from pydantic import ValidationError
from typing import Dict, Any
from db_schema import Address, HolidayRecord, IllnessRecord, Patient
from base import Base


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
        # print(f"Decoded data: {data}")
        source = data.get('source')
        value = data.get('value')
        patient_id = value.get('Patient_ID')
        
        if value is None or patient_id is None:
            self.logger.error(f"Failed to process data: No value or patient ID found")
            raise self.DataProcessingError("Missing value or patient ID")

        try:
            # Process the data based on the source and add to processed_message
            if source == 'patient_records':
                self.process_patient_data(value, processed_message)
            elif source == 'holiday_records':
                self.process_holiday_data(value, processed_message)
            elif source == 'illness_records':
                self.process_illness_data(value, processed_message)
        except ValidationError as e:
            self.logger.error(f"Failed to validate data: {e}")
            raise self.DataProcessingError("Validation error")
        
        processed_message.add_data('patient_id', patient_id)

    def process_patient_data(self, value: Dict[str, Any], processed_message) -> None:
        """
        Process the patient data and add it to the processed_message object.

        Args:
        value (dict): The value containing patient data from the raw message.
        processed_message (ProcessedMessage): The object to which processed data should be added.
        """
        
        # Extract address details and remove them from the value dictionary
        street = value.pop('Straße', None)
        city = value.pop('Stadt', None)
        postal_code = value.pop('Postleitzahl', None)
        
        # Create a Patient instance using the remaining data in value
        try:
            patient_data = Patient(**value)
            
            # If address details were found, create an Address instance and add it to the patient_data
            if street and city and postal_code:
                address = Address(Straße=street, Stadt=city, Postleitzahl=postal_code)
                patient_data.address = address
            # Add the Patient object to the processed_message
            processed_message.add_data('value', patient_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise

    def process_holiday_data(self, value: Dict[str, Any], processed_message) -> None:
        """
        Process the holiday data and add it to the processed_message object.

        Args:
        value (dict): The value containing holiday data from the raw message.
        processed_message (ProcessedMessage): The object to which processed data should be added.
        """
        try:
            holiday_data = HolidayRecord(**value)
            processed_message.add_data('value', holiday_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise

    def process_illness_data(self, value: Dict[str, Any], processed_message) -> None:
        """
        Process the illness data and add it to the processed_message object.

        Args:
        value (dict): The value containing illness data from the raw message.
        processed_message (ProcessedMessage): The object to which processed data should be added.
        """
        try:
            illness_data = IllnessRecord(**value)
            processed_message.add_data('value', illness_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise



