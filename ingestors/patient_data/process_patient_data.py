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
            validated_data = self.validate_data(source, value)

            # if condition to check if validated_data is patient_data
            if 'patient_data' in validated_data and 'address' in validated_data:
                self.process_patient_data(validated_data, processed_message)
            elif 'holiday_data' in validated_data:
                self.process_holiday_data(validated_data['holiday_data'], processed_message)
            elif 'illness_data' in validated_data:
                self.process_illness_data(validated_data['illness_data'], processed_message)
            else:
                self.logger.warning(f"Unknown source: {source}")
                raise self.DataProcessingError("Unknown source")
            
        except ValidationError as e:
            self.logger.error(f"Failed to validate data: {e}")
            raise self.DataProcessingError("Validation error")
        
        processed_message.add_data('patient_id', patient_id)

    def process_patient_data(self, validated_data: Dict[str, Any], processed_message) -> None:
        
        try:
            patient_data = validated_data['patient_data']
            address = validated_data['address']
            patient_data.address = address
            # Add the Patient object to the processed_message
            processed_message.add_data('value', patient_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise


    def validate_data(self, source: str, value: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data based on the source using the appropriate Pydantic model.
        """
        try:
            if source == 'patient_records':
                # Extract and validate address details if present
                address_details = {k: value.pop(k, None) for k in ['Straße', 'Stadt', 'Postleitzahl']}
                address = None
                if all(address_details.values()):
                    address = Address(**address_details)
                
                # Validate the rest of the patient data
                patient_data = Patient(**value)
                return {"patient_data": patient_data, "address": address}
            
            elif source == 'holiday_records':
                holiday_data = HolidayRecord(**value)
                return {"holiday_data": holiday_data}
            
            elif source == 'illness_records':
                illness_data = IllnessRecord(**value)
                return {"illness_data": illness_data}
            
            # Add validation for other sources as needed
            else:
                self.logger.warning(f"Unknown source: {source}")
                return {}  # Return an empty dictionary for unknown sources
            
            # Add validation for other sources as needed
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def process_holiday_data(self, holiday_data: Dict[str, Any], processed_message) -> None:
        
        try:
            processed_message.add_data('value', holiday_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise

    def process_illness_data(self, illness_data: Dict[str, Any], processed_message) -> None:
        try:
            processed_message.add_data('value', illness_data)
        except ValidationError as e:
            self._handle_exception(e)
            raise



