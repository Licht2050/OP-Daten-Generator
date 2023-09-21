import os
import sys

from pydantic import ValidationError
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb'))
])

from typing import Dict, Any
from indoor_environment_data_schema import IndoorEnvironmentDataStatus, IndoorEnvironmentDataValue

from base import Base


class DataProcessor(Base):
    def __init__(self):
        super().__init__()
        self._setup_logging()
        pass

    def process_data(self, processed_message):
        """Process data before writing to database """
        data = processed_message.raw_message
        value = data.get('value')
        try:
            # print(f"Processing data: {data.raw_message}")
            self.validate_data(data)

            indoor_environment_value = IndoorEnvironmentDataValue(**value)
            processed_message.add_data('value', indoor_environment_value)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def validate_data(self, data):
        """Validate data before writing to database """
        try:
            IndoorEnvironmentDataStatus(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

