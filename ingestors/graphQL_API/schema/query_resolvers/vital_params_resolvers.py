
import os
import sys
import logging
from ariadne import ObjectType
import uuid
from cassandra.query import named_tuple_factory


from usable_functions.usable_functions import calculate_average_value, get_requested_subfields, initialize_patient_data



sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../db_connectors'),
    os.path.join(os.path.dirname(__file__), '../../../schema/cql'),
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../helper'))
])


from paths_config import (BLOOD_PRESSURE_DIASTOLIC_HIGH, BLOOD_PRESSURE_DIASTOLIC_LOW,
                        BLOOD_PRESSURE_SYSTOLIC_HIGH, BLOOD_PRESSURE_SYSTOLIC_LOW,
                        BISPIRAL_INDEX_HIGH, BISPIRAL_INDEX_LOW,
                        ETCO2_HIGH, ETCO2_LOW,
                        HEART_RATE_HIGH, HEART_RATE_LOW,
                        OXYGEN_SATURATION_HIGH, OXYGEN_SATURATION_LOW,
                        STATUS_HIGH, STATUS_LOW,
                        STATUS_NORMAL, STATUS_UNKNOWN,
)
from cql_loader import CQLLoader
from config_loader import ConfigLoader
from paths_config import (
    CONFIG_FILE_PATH,
    VITAL_PARAMS_TABLE_DEFFINATION_PATH
)
from cassandra_connector import CassandraConnector


# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


config_loader = ConfigLoader(CONFIG_FILE_PATH)
cassandra_config = config_loader.load_config('cassandra')

# Load CQL table definition
schema_path = os.path.join(os.path.dirname(__file__), '../../../schema/cql/vital_params_schema.cql')
cql_loader = CQLLoader(schema_path)
table_definition = cql_loader.get_commands(category="Schema")


try:
    cassandra_connector = CassandraConnector(cassandra_config['nodes'])
    print("Cassandra connector initialized===========================")
except Exception as e:
    logger.error(f"Error initializing InfluxDB connector: {e}")
    raise e







vital_params_query = ObjectType("VitalParamsByDate")



@vital_params_query.field("getVitalParamsByDate")
def resolve_get_vital_params_by_date(root, info, patientId, timestamp, secondsRange):
    patient_id_uuid, start_timestamp, end_timestamp = initialize_patient_data(patientId, timestamp, secondsRange)
    requested_vital_params = get_requested_subfields(info.field_nodes[0], "vitalParams")
    result = {'vitalParams': {}}

    try:
        if 'heartRate' in requested_vital_params:
            heart_rate_params = requested_vital_params.get("heartRate")
            heart_rate_entry = fetch_and_process_vital_params(patient_id_uuid, timestamp, start_timestamp, end_timestamp, 'heart_rate', 'heart_rate', HEART_RATE_LOW, HEART_RATE_HIGH, heart_rate_params)
            result['vitalParams']['heartRate'] = heart_rate_entry
        
        if 'oxygenSaturation' in requested_vital_params:
            oxygen_saturation_params = requested_vital_params.get("oxygenSaturation")
            oxygen_saturation_entry = fetch_and_process_vital_params(patient_id_uuid, timestamp, start_timestamp, end_timestamp, 'oxygen_saturation', 'oxygen_saturation', OXYGEN_SATURATION_LOW, OXYGEN_SATURATION_HIGH, oxygen_saturation_params)
            result['vitalParams']['oxygenSaturation'] = oxygen_saturation_entry
        
        if 'bispectralIndex' in requested_vital_params:
            bispectral_index_params = requested_vital_params.get("bispectralIndex")
            bispectral_index_entry = fetch_and_process_vital_params(patient_id_uuid, timestamp, start_timestamp, end_timestamp, 'bispectral_index', 'bispectral_index', BISPIRAL_INDEX_LOW, BISPIRAL_INDEX_HIGH, bispectral_index_params)
            result['vitalParams']['bispectralIndex'] = bispectral_index_entry
        if 'bloodPressure' in requested_vital_params:
            blood_pressure_params = requested_vital_params.get("bloodPressure")
            blood_pressure_entry = fetch_and_process_blood_pressure(patient_id_uuid, timestamp, start_timestamp, end_timestamp, blood_pressure_params, 'blood_pressure')
            result['vitalParams']['bloodPressure'] = blood_pressure_entry
        if 'etco2' in requested_vital_params:
            etco2_params = requested_vital_params.get("etco2")
            etco2_entry = fetch_and_process_vital_params(patient_id_uuid, timestamp, start_timestamp, end_timestamp, 'etco2', 'etco2', ETCO2_LOW, ETCO2_HIGH, etco2_params)
            result['vitalParams']['etco2'] = etco2_entry
         

        return result

    except Exception as e:
        logging.error(f"Error retrieving heart rate data: {e}")
        raise e
    








def fetch_vital_params(patien_id_uuid, start_timestamp, end_timestamp, table_name, requested_fields="*"):
    session = cassandra_connector.connect(keyspace='medical_data')
    session.row_factory = named_tuple_factory
    fields_str = ', '.join(requested_fields)
    query = f"SELECT {fields_str} FROM medical_data.{table_name} WHERE Patient_ID = ? AND timestamp >= ? AND timestamp <= ? ALLOW FILTERING"
    prepared = session.prepare(query) 
    return session.execute(prepared.bind([patien_id_uuid, start_timestamp, end_timestamp]))






def fetch_and_process_vital_params(patient_id_uuid, timestamp, start_timestamp, end_timestamp, table_name, key, low, high, requested_fields):
    data = [row._asdict() for row in fetch_vital_params(patient_id_uuid, start_timestamp, end_timestamp, table_name, requested_fields)]
    avg = calculate_average_value(data, key)
    status = calculate_status(avg, low, high)
    entry = {}
    if data:
        for field in requested_fields:
            if field == key:
                entry[field] = avg
            elif field == 'timestamp':
                entry[field] = timestamp
            elif field == 'status':
                entry[field] = status
            else:
                entry[field] = data[0].get(field)
    return entry or None


def fetch_and_process_blood_pressure(patient_id_uuid, timestamp, start_timestamp, end_timestamp, blood_pressure_params, table_name='blood_pressure'):
    data = [row._asdict() for row in fetch_vital_params(patient_id_uuid, start_timestamp, end_timestamp, table_name,  blood_pressure_params)]
    
    avg_systolic = calculate_average_value(data, 'systolic')
    status_systolic = calculate_status(avg_systolic, BLOOD_PRESSURE_SYSTOLIC_LOW, BLOOD_PRESSURE_SYSTOLIC_HIGH)

    avg_diastolic = calculate_average_value(data, 'diastolic')
    status_diastolic = calculate_status(avg_diastolic, BLOOD_PRESSURE_DIASTOLIC_LOW, BLOOD_PRESSURE_DIASTOLIC_HIGH)
    
    if data:
        entry = data[0]
        entry['systolic'] = avg_systolic
        entry['diastolic'] = avg_diastolic
        entry['timestamp'] = timestamp
        entry['status'] = f"systolic: {status_systolic}/diastolic:{status_diastolic}"
    else:
        entry = None
    return entry

def calculate_status(value, low_threshold, high_threshold):
    if value < low_threshold:
        return STATUS_LOW
    elif value > high_threshold:
        return STATUS_HIGH
    return STATUS_NORMAL


