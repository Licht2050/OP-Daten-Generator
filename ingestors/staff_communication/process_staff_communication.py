import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))

from base import Base


class DataProcessor(Base):
    def __init__(self):
        super().__init__()
        self._setup_logging()
        pass

    def process_data(self, data):
        """Process data before writing to database """
        # message_dict = self._decode_message(data)
        # print(f"Processing data -============: {data.raw_message}")
        processed_data = data.raw_message
        return processed_data
