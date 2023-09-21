import os
import sys

from pydantic import ValidationError
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'),
    os.path.join(os.path.join(os.path.dirname(__file__), '../schema/influxdb'))
])

from typing import Dict, Any
from entry_exit_events_schema import EntryExitEvent

from base import Base


class DataProcessor(Base):
    def __init__(self):
        super().__init__()
        self._setup_logging()
        pass

    def process_data(self, data):
        """Process data before writing to database """
        try:
            # print(f"Processing data: {data.raw_message}")
            self.validate_data(data.raw_message)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def validate_data(self, data):
        """Validate data before writing to database """
        try:
            EntryExitEvent(**data)
        except ValidationError as e:
            self.logger.error(f"Data validation error: {e}")
            raise
