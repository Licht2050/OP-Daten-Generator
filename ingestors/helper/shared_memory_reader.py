import logging  
import mmap
import struct
import posix_ipc
from typing import Tuple, Union, Any


class SharedMemoryReader:
    def __init__(self, config):
        if config:
            self.config = config
            self._setup_logging()
        else:
            raise RuntimeError("No config provided.")
        
        self.shared_memory_path = self.config['shared_memory_path']
        self.sem = posix_ipc.Semaphore("MySemaphore")
        self.data_format = self.config['data_format']
        self.buffer_size = self.config['buffer_size']

        self.f = None
        self.mm = None

    def _setup_logging(self):
        """Initialize logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def open(self) -> None:
        """Open the shared memory for reading."""
        self.f = open(self.shared_memory_path, "r+b")
        self.mm = mmap.mmap(self.f.fileno(), self.buffer_size, access=mmap.ACCESS_READ)

    def read_data(self)-> Union[Tuple[Any, ...], None]:
        """Read data from the shared memory."""
        data_tuple = None
        if self.mm is None:
            raise RuntimeError("Shared memory not opened. Call open() first.")
        
        try:
            # wait for semaphore
            self.sem.acquire(1.0)

            # Reset position to beginning
            self.mm.seek(0)

            # Unpack the data based on the format defined in the config
            data_tuple = struct.unpack(self.data_format, self.mm.read(self.buffer_size))

            # Release the semaphore
            self.sem.release()
        except posix_ipc.BusyError:
            self.logger.info("Semaphore is busy.")
            

        return data_tuple

    def close(self):
        """Close all resources."""
        for resource in [self.mm, self.f, self.sem]:
            if resource:
                resource.close()
        
        self.mm, self.f = None, None