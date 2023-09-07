import mmap
import struct
from time import sleep
import json


class SharedMemoryReader:
    def __init__(self, config_file):
        # Load the JSON configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.shared_memory_path = self.config['shared_memory_path']
        self.data_format = self.config['data_format']
        self.buffer_size = self.config['buffer_size']

        self.f = None
        self.mm = None

    def open(self):
        # Open the file and mmap
        self.f = open(self.shared_memory_path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), self.buffer_size, access=mmap.ACCESS_READ)

    def read_data(self):
        if self.mm is None:
            raise RuntimeError("Shared memory not opened. Call open() first.")
        
        # Reset position to beginning
        self.mm.seek(0)

        # Unpack the data based on the format defined in the config
        data_tuple = struct.unpack(self.data_format, self.mm.read(self.buffer_size))
        
        return data_tuple

    def close(self):
        if self.mm:
            self.mm.close()
        if self.f:
            self.f.close()

        self.mm = None
        self.f = None

if __name__ == "__main__":
    reader = SharedMemoryReader("config.json")
    
    try:
        reader.open()
        while True:
            data = reader.read_data()
            print("Message Duration:", data[0])
            print("Offset:", data[1])
            sleep(1)
    except KeyboardInterrupt:
        print("Stopping reader.")
    finally:
        reader.close()
