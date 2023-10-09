from datetime import timedelta
import os
import sys
import logging
from ariadne import ObjectType, QueryType

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../db_connectors')
])


# Imports
from mongodb_conncetor import MongoDBConnector
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH
from dateutil.parser import parse

# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


config_loader = ConfigLoader(CONFIG_FILE_PATH)
mongodb_config = config_loader.load_config('op_details')


try:
    mongodb_connector = MongoDBConnector(
        host=mongodb_config['host'],
        port=mongodb_config['port'],
        database_name=mongodb_config['database'],
        collection_name=mongodb_config['collection']
    )
except Exception as e:
    logger.error(f"Error initializing MongoDB connector: {e}")
    raise e


op_details_query = ObjectType("OpDetailsQuery")


@op_details_query.field("getOpDetailsById")
def resolve_get_op_details_by_id(root, info, patient_id):
    print("Resolver getOpDetailsById aufgerufen")

    try:
        op_details = mongodb_connector.find_data({'patient_id': patient_id})
        return op_details
    except Exception as e:
        logger.error(f"Error getting op_details: {e}")
        raise e