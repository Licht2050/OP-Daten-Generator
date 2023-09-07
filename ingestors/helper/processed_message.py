class ProcessedMessage:
    def __init__(self, raw_message):
        self.raw_message = raw_message
        self.additional_data = {}

    def add_data(self, key, value):
        self.additional_data[key] = value

    def get_data(self, key):
        return self.additional_data.get(key, None)
    
    def to_dict(self):
        """Converts the raw_message and additional_data to a single dictionary."""
        result_dict = self.raw_message.copy()  # Start with a copy of raw_message
        result_dict.update(self.additional_data)  # Add additional_data to it
        return result_dict