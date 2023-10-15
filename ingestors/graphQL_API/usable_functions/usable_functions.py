from datetime import datetime, timedelta
import uuid
import logging

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


def str_to_datetime(timestamp_str):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(timestamp_str, datetime_format)

def calculate_time_range(timestamp_datetime, seconds_range):
    start_timestamp = timestamp_datetime - timedelta(seconds=seconds_range)
    end_timestamp = timestamp_datetime + timedelta(seconds=seconds_range)
    return start_timestamp, end_timestamp



def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def calculate_average_value(data, key):
    values = [result[key] for result in data]
    return round(calculate_average(values))


def get_requested_subfields(node, target_main_field=None):
    fields = {} 
    if not node.selection_set:
        return fields
    
    for selection in node.selection_set.selections:
        field_name = selection.name.value
        if selection.selection_set:
            if target_main_field is None or field_name == target_main_field:
                subfields = get_requested_subfields(selection)
                if field_name == target_main_field:
                    return subfields
                fields[field_name] = list(subfields.keys())
        else:
            fields[field_name] = None
    return fields


def get_requested_fields(info):
    # Überprüfe, welche Felder der Client angefordert hat
    requested_fields = info.field_nodes[0].selection_set.selections
    requested_field_names = [field.name.value for field in requested_fields]
    return requested_field_names


# def get_requested_subfields(info, main_field_name, subfield_name):
#     # Durchsucht alle Feldknoten
#     fields = {}
#     for node in info.field_nodes:
#         # Prüft, ob der aktuelle Knotenname mit main_field_name übereinstimmt
#         # if node.name.value == main_field_name:
#             # Durchsucht die Auswahlmenge des Knotens, um die Unterfelder zu erhalten
#         if node.selection_set:
#             # Extrahiert die Unterfelder von "vitalParams"
#             for selection in node.selection_set.selections:
#                 if selection.name.value == subfield_name and selection.selection_set:
#                     return [field.name.value for field in selection.selection_set.selections]
#     return []



def convert_to_mongo_projection(projection_data):
    mongo_projection = {}
    if isinstance(projection_data, dict):
        for key, values in projection_data.items():
            if values is None:
                mongo_projection[key] = 1
            elif isinstance(values, list):
                for value in values:
                    mongo_key = f"{key}.{value}"
                    mongo_projection[mongo_key] = 1
    elif isinstance(projection_data, list):
        for value in projection_data:
            mongo_projection[value] = 1
    else:
        raise ValueError("Expected a dictionary or list, but received a {}".format(type(projection_data)))
    
    return mongo_projection


def initialize_patient_data(patientId, timestamp, secondsRange):
    patient_id_uuid = uuid.UUID(patientId)
    timestamp_datetime = str_to_datetime(timestamp)
    if secondsRange == None:
        secondsRange = 1
    start_timestamp, end_timestamp = calculate_time_range(timestamp_datetime, secondsRange)
    return patient_id_uuid, start_timestamp, end_timestamp





def fetch_data_from_influx(influxdb_connector, table_name, start_timestamp, end_timestamp, requested_params, additional_filters=None):

    filters = [f"time >= '{start_timestamp}'", f"time <= '{end_timestamp}'"]
    if additional_filters:
        filters.extend(additional_filters)

    # Convert the requested_params list to a comma-separated string
    param_string = ', '.join(requested_params)
    correlated_table_name = f"correlated_{table_name}"
    query_filters = " AND ".join(filters)
    query = f"SELECT {param_string} FROM {correlated_table_name} WHERE {query_filters}"
    result_set = influxdb_connector.query(query)

    # print("query: "+ str(query))
    
    if not result_set:
        logger.warning("No data found for the query.")
        return None

    data_list = list(result_set.get_points(measurement=correlated_table_name))
    if not data_list:
        logger.warning("No points found in the data set.")
        return None

    return data_list

