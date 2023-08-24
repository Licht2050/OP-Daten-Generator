# 2. Write a class to connect to mongodb and return the connection object
# Path: OP-Daten-Generator/ingestors/db_connectors/mongodb_conncetor.py

import pymongo
import logging

class MongoDBConnector:
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
        self.host = host
        self.port = port
        self.database_name = database_name
        self.collection_name = collection_name

    def connect(self):
        """
        Connects to the MongoDB instance and returns the connection object.
        
        Returns:
            pymongo.MongoClient: The MongoDB connection object.
        """
        try:
            client = pymongo.MongoClient(f"mongodb://{self.host}:{self.port}/")
            return client
        except Exception as e:
            logging.error(f"Error during MongoDB connection: {e}")
            raise e