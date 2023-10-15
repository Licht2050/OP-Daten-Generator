from datetime import timedelta
import os
import sys
import logging
import uuid

from ariadne import ObjectType


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../db_connectors')
])

from mongodb_conncetor import MongoDBConnector
from influxdb_connector import InfluxDBConnector
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH
from usable_functions.usable_functions import calculate_average, calculate_average_value , calculate_time_range, convert_to_mongo_projection, fetch_data_from_influx, get_requested_subfields, initialize_patient_data

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


config_loader = ConfigLoader(CONFIG_FILE_PATH)
influxdb_config = config_loader.load_config("influxdb")
mongodb_config = config_loader.load_config('holiday_records')


try:
    influxdb_connector = InfluxDBConnector(**influxdb_config)
except Exception as e:
    logger.error(f"Error initializing InfluxDB connector: {e}")
    raise e


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


external_factors_query = ObjectType("ExternalFactorsQuery")


EXCLUDED_FIELDS = ["patient_id", "time"]


@external_factors_query.field("getOutdoorEnvironmentByTimeAndPid")
def resolve_get_outdoor_environment_by_time_and_pid(root, info, patientId, timestamp, secondsRange):
    print("Resolver getOutdoorEnvironmentByTimeAndPid aufgerufen")

    try:
        patient_id_uuid, start_timestamp, end_timestamp = initialize_patient_data(patientId, timestamp, secondsRange)

        requested_vital_params = get_requested_subfields(info.field_nodes[0], "externalFactros")
        print("requested_vital_params: "+ str(requested_vital_params))
        result = {}

        if "outdoorEnvironment" in requested_vital_params:
            outdoor_envrionment_params = requested_vital_params.get("outdoorEnvironment")
            additional_filters = [f"patient_id = '{patient_id_uuid}'"]

            outdoor_envrionment_data = fetch_data_from_influx(influxdb_connector, "outdoor_environment", start_timestamp, end_timestamp, outdoor_envrionment_params , additional_filters)
            # print("outdoor_envrionment_data: "+ str(outdoor_envrionment_data))

            if outdoor_envrionment_data:
                averages = {}
                for param in outdoor_envrionment_params:
                    if param not in EXCLUDED_FIELDS:
                        values = [entry[param] for entry in outdoor_envrionment_data]
                        # print("values: "+ str(values))
                        averages[param] = round(calculate_average(values))
                result["outdoorEnvironment"] = averages

        if "holidayRecords" in requested_vital_params:
            holiday_records_params = {}
            holiday_records_params["records"] = requested_vital_params.get("holidayRecords")
            
            additional_filters = [f"patient_id = '{patient_id_uuid}'"]

            projection = convert_to_mongo_projection(holiday_records_params)
            holiday_records = mongodb_connector.find_data({'patient_id': patientId}, projection)
            print("projection: "+ str(holiday_records))
            result["holidayRecords"] = holiday_records["records"]

        return result
    except Exception as e:
        logger.error(f"Error getting all indoor environment data: {e}")
        raise e