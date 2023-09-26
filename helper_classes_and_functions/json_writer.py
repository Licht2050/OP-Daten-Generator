import json

class JSONWriter:
    """
    A class for writing JSON data to a file.
    """
    """
    A class for 
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def write_data(self, data_str):
        # data_obj = json.loads(data_str)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_str, f, ensure_ascii=False, indent=4)
