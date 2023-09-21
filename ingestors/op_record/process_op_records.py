from datetime import datetime
import os
import sys

from pydantic import ValidationError


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/mongodb'))
])

from typing import Dict, Any
from db_schema import PostOPRecord, PreOPRecord

from base import Base


class DataProcessor(Base):
    def __init__(self):
        super().__init__()
        self._setup_logging()
        pass

    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message
        try:
            # Formatting the 'Duration' field
            duration_str = data.get('value').get('Duration')
            if duration_str:
                data['value']['Duration'] = int(duration_str.split()[0])

            # Formatting the 'Date' field
            date_str = data.get('value').get('Date')
            if date_str:
                data['value']['Date'] = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')

            # print(f"Processing data: {data.raw_message}")
            validated_data = self.validate_data(data)
            if validated_data:
                processed_message.add_data('value', validated_data.get('value'))
                processed_message.add_data('patient_id', validated_data.get('patient_id'))
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def validate_data(self, data):
        """Validate data before writing to database """
        source_to_class_map = {
            'pre_op_record' : PreOPRecord,
            'post_op_record': PostOPRecord
        }
        source = data.get('source')
        patient_id = data.get('value').pop('Patient_ID')
        try:
            if source in source_to_class_map:
                record_class = source_to_class_map[source]
                validated_data = record_class(**data.get('value'))
                return {'patient_id': patient_id, 'value': validated_data}
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise
