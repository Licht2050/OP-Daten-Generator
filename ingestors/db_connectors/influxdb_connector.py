import os
import sys
from influxdb import InfluxDBClient


# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))
from base import Base
from config_loader import ConfigLoader
from config import CONFIG_FILE_PATH

class InfluxDBConnector(Base):
    """Class to connect to InfluxDB and perform basic operations."""
    
    def __init__(self, host='localhost', port=8086, username='', password='', database=None):
        """Initialize connection to InfluxDB
        
        Args:
            host (str): Host address. Defaults to 'localhost'.
            port (int): Port number. Defaults to 8086.
            username (str): Username. Defaults to an empty string.
            password (str): Password. Defaults to an empty string.
            database (str): Database name to connect to. Defaults to None.
        """
        super().__init__()  # Call Base class constructor to setup logging and other common functionalities
        self._setup_logging()
        try:
            self.client = InfluxDBClient(host=host, port=port, username=username, password=password)
            if database:
                self.client.switch_database(database)
        except Exception as e:
            self._handle_exception(f"Failed to connect to InfluxDB: {e}")
    
    def write_points(self, json_body):
        """Write points to InfluxDB
        
        Args:
            json_body (list): List of dictionaries containing the points to write.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            return self.client.write_points(json_body)
        except Exception as e:
            self._handle_exception(f"Failed to write points: {e}")
            return False
    
    def query(self, query_str):
        """Query data from InfluxDB
        
        Args:
            query_str (str): Query string to execute.
            
        Returns:
            ResultSet: Query result.
        """
        try:
            return self.client.query(query_str)
        except Exception as e:
            self._handle_exception(f"Failed to execute query: {e}")
            return None
    
    def create_database(self, db_name):
        """Create a new database
        
        Args:
            db_name (str): Name of the database to create.
        """
        try:
            self.client.create_database(db_name)
        except Exception as e:
            self._handle_exception(f"Failed to create database: {e}")
    
    def list_databases(self):
        """List all databases
        
        Returns:
            list: List of databases.
        """
        try:
            return self.client.get_list_database()
        except Exception as e:
            self._handle_exception(f"Failed to list databases: {e}")
            return []


if __name__ == "__main__":
    config_loader = ConfigLoader(CONFIG_FILE_PATH)
    config = config_loader.load_config("influxdb")
    
    influx_connector = InfluxDBConnector(host=config['host'] , port=config['port'] , database=config['database'])
    
    # Writing data
    json_body = [
        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "fields": {
                "value": 0.64
            }
        }
    ]
    influx_connector.write_points(json_body)
    
    print("List of databases:", influx_connector.list_databases())

    # Querying data
    result = influx_connector.query("SELECT * FROM cpu_load_short")
    print("Query Result:", result)
