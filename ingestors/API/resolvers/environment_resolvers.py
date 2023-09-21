from datetime import timedelta
import os
import sys
import logging


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../config'),
    os.path.join(os.path.dirname(__file__), '../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../db_connectors')
])


from influxdb_connector import InfluxDBConnector
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


config_loader = ConfigLoader(CONFIG_FILE_PATH)
influxdb_config = config_loader.load_config("influxdb")

try:
    influxdb_connector = InfluxDBConnector(**influxdb_config)
except Exception as e:
    logger.error(f"Error initializing InfluxDB connector: {e}")
    raise e


def resolve_get_all_indoor_environment_data(root, info):
    """
    Resolver function for the getAllIndoorEnvironmentData query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        
    Returns:
        list: A list of dictionaries containing the indoor environment data.
    """
    try:
            query = "SELECT * FROM indoor_environment_data"
            indoor_environment_data_result_set = influxdb_connector.query(query)
            
            if not indoor_environment_data_result_set:
                logger.warning("No data found for the query.")
                return None
            
            # Extract the data from the ResultSet object
            indoor_environment_data_list = list(indoor_environment_data_result_set.get_points(measurement='indoor_environment_data'))
            
            if not indoor_environment_data_list:
                logger.warning("No points found in the data set.")
                return None

            return indoor_environment_data_list
    except Exception as e:
        logger.error(f"Error getting all indoor environment data: {e}")
        raise e


