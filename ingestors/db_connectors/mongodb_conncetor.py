import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
from pymongo import MongoClient, errors

from base import Base

class MongoDBConnector(Base):
    """
    A class to connect to MongoDB and return the connection object.
    """
    def __init__(self, host, port, database_name, collection_name):
        """
        Initializes the MongoDBConnector class.
        
        Args:
            host (str): The host name of the MongoDB instance.
            port (int): The port number of the MongoDB instance.
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
        """
        super().__init__()
        self._setup_logging()
        self.host = host
        self.port = port
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = self.connect()

    def connect(self):
        """
        Connects to the MongoDB instance and returns the connection object.
        
        Returns:
            pymongo.MongoClient: The MongoDB connection object.
        """
        max_retries = 3
        retry_delay = 5  # seconds
        for attempt in range(max_retries):
            try:
                client = MongoClient(f"mongodb://{self.host}:{self.port}/", serverSelectionTimeoutMS=5000)
                client.server_info()  # Trigger a call to the server to verify the connection
                self.logger.info(f"Successfully connected to MongoDB on attempt {attempt + 1}")
                return client
            except ConnectionError as e:
                self._handle_exception(f"Error during connection to MongoDB on attempt {attempt + 1}: {e}")
                if attempt + 1 < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise e
            
    def get_collection(self):
        try:
            if self.client:
                db = self.client[self.database_name]
                collection = db[self.collection_name]
                return collection
            else:
                raise Exception("No connection to MongoDB")
        except Exception as e:
            self._handle_exception(f"Error during collection retrieval: {e}")
            raise e
    
    def insert_data(self, data):
        collection = self.get_collection()
        try:
            result = collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            self._handle_exception(f"Error during data insertion: {e}")
            raise e

    def find_data(self, query, projection=None):
        collection = self.get_collection()
        try:
            result = collection.find_one(query, projection)
            return result
        except Exception as e:
            self._handle_exception(f"Error during data retrieval: {e}")
            raise e
    
    def find_all_data(self, query):
        collection = self.get_collection()
        try:
            result = collection.find(query)
            return list(result)
        except Exception as e:
            self._handle_exception(f"Error during data retrieval: {e}")
            raise e
    



    def update_data(self, query, new_values, update_many=False):
        collection = self.get_collection()
        try:
            if update_many:
                result = collection.update_many(query, new_values)
            else:
                result = collection.update_one(query, new_values)
            return result.modified_count
        except Exception as e:
            self._handle_exception(f"Error during data update: {e}")
            raise e

    def delete_data(self, query):
        collection = self.get_collection()
        try:
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            self._handle_exception(f"Error during data deletion: {e}")
            raise e

    def create_index(self, keys, **kwargs):
        collection = self.get_collection()
        try:
            collection.create_index(keys, **kwargs)
        except Exception as e:
            self._handle_exception(f"Error during index creation: {e}")
            raise e
        
    def close(self):
        if self.client:
            self.client.close()

    