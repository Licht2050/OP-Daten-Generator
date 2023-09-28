# data_publisher/data_publisher_singleton.py
from data_publisher import DataPublisher



class DataPublisherSingleton:
    _instance = None
    
    @staticmethod
    def get_instance():
        if DataPublisherSingleton._instance is None:
            DataPublisherSingleton._instance = DataPublisher()
        return DataPublisherSingleton._instance
