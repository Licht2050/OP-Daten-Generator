class ProcessedMessage:
    def __init__(self, raw_message):
        self.raw_message = raw_message
        self.additional_data = {}

    def add_data(self, key, value):
        self.additional_data[key] = value

    def get_data(self, key):
        return self.additional_data.get(key, None)