from datetime import timedelta
import os
import sys
import logging
import uuid

from ariadne import ObjectType, QueryType


sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../db_connectors')
])


from influxdb_connector import InfluxDBConnector
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH
from usable_functions.usable_functions import calculate_average, calculate_average_value , calculate_time_range, fetch_data_from_influx, get_requested_subfields, initialize_patient_data

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



environment_data_query = ObjectType("EnvironmentDataQuery")
op_environment_data_by_timestamp_and_pid = ObjectType("OpEnvironmentTimestampByDateAndPID")

# @environment_data_query.field("environmentData")
@environment_data_query.field("getIndoorEnvironmentData")
def resolve_get_allIndoor_environment_data(root, info):
    print("Debug: Resolver getAllIndoorEnvironmentData aufgerufen")
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




EXCLUDED_FIELDS = ["door_status", "patient_id"]

@op_environment_data_by_timestamp_and_pid.field("getOpEnvironmentByTimestampAndPID")
def resolve_get_op_environment_data_by_date_and_pid(root, info, pid: str, timestamp: str, secondsRange: int):
    print("Debug: Resolver getOpEnvironmentByTimestampRoomAndPID aufgerufen")
    try:
        patient_id_uuid, start_timestamp, end_timestamp = initialize_patient_data(pid, timestamp, secondsRange)
        requested_vital_params = get_requested_subfields(info.field_nodes[0], "opEnvironment")
        result = {}

        if "indoorEnvironment" in requested_vital_params:
            indoor_environment_data_params = requested_vital_params.get("indoorEnvironment")
            additional_filters = [f"patient_id = '{patient_id_uuid}'"]

            indoor_environment_datas = fetch_data_from_influx(influxdb_connector, "indoor_environment_data", start_timestamp, end_timestamp, indoor_environment_data_params, additional_filters)
            # print("indoor_environment_datas: "+ str(indoor_environment_datas))

            if indoor_environment_datas:
                averages = {}
                for param in indoor_environment_data_params:
            
                    if should_calculate_field(param):
                        values = [entry[param] for entry in indoor_environment_datas]
                        averages[param] = round(calculate_average(values))
                    elif param == "door_status" and indoor_environment_datas:
                        # Get the last value for door_status
                        averages[param] = indoor_environment_datas[-1][param]

                result["indoorEnvironment"] = averages
            else:
                result["indoorEnvironment"] = None        
        if "entryExitEvents" in requested_vital_params:
            entry_exit_events_params = requested_vital_params.get("entryExitEvents")
            additional_filters = [f"patient_id = '{patient_id_uuid}'"]

            entry_exit_events = fetch_data_from_influx(influxdb_connector, "entry_exit_events", start_timestamp, end_timestamp, entry_exit_events_params, additional_filters)
            # print("entry_exit_events: "+ str(entry_exit_events[-1]))
            if entry_exit_events:
                entry = {}
                for param in entry_exit_events_params:
                    entry[param] = entry_exit_events[-1][param]
            result["entryExitEvents"] = entry

        
        if "staffCommunication" in requested_vital_params:
            staff_communication_params = requested_vital_params.get("staffCommunication")
            additional_filters = [f"patient_id = '{patient_id_uuid}'"]

            staff_communication = fetch_data_from_influx(influxdb_connector, "staff_communication", start_timestamp, end_timestamp, staff_communication_params, additional_filters)
            # print("staff_communication: "+ str(staff_communication[-1]))
            if staff_communication:
                entry = {}
                for param in staff_communication_params:
                    entry[param] = staff_communication[-1][param]
            result["staffCommunication"] = entry

        return result

    except Exception as e:
        logger.error(f"Error getting all indoor environment data: {e}")
        raise e


def should_calculate_field(field_name):
    return field_name not in EXCLUDED_FIELDS




