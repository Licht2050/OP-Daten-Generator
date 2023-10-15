from datetime import timedelta
import os
import sys
import logging
from ariadne import ObjectType

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
from usable_functions.usable_functions import convert_to_mongo_projection, get_requested_subfields

# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')


config_loader = ConfigLoader(CONFIG_FILE_PATH)
mongodb_config = config_loader.load_config('mongodb')

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


patient_query = ObjectType("PatientQuery")


@patient_query.field("getPatientById")
def resolve_get_patient_by_id(root, info, patient_id):
    print("Resolver getPatientById aufgerufen")  # Logging
    """
    Resolver function for the getPatientById query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        patient_id (str): The ID of the patient to get.
    
    Returns:
        dict: A dictionary containing the patient data.
    """
    try:
        requested_fields = get_requested_subfields(info.field_nodes[0], "patientProfile")
        projection = convert_to_mongo_projection(requested_fields)
        patient = mongodb_connector.find_data({'patient_id': patient_id}, projection)
        return patient
    except Exception as e:
        print(f"Error getting patient by ID: {e}")
        raise e


@patient_query.field("getAllPatients")
def resolve_get_all_patients(root, info):
    """
    Resolver function for the getAllPatient query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        
    Returns:
        list: A list of dictionaries containing the patient data.
    """
    try:
        patients = mongodb_connector.find_all_data({})
        vitalparameter = None

        return patients, vitalparameter
    except Exception as e:
        print(f"Error getting all patients: {e}")
        raise e

@patient_query.field("getAllPatientByOpRoom")
def resolve_get_all_patient_by_op_room(root, info, op_room):
    """
    Resolver function for the getPatientByOperationRoom query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        operation_room (str): The operation room to get the patient for.
    
    Returns:
        dict: A dictionary containing the patient data.
    """
    try:
        patients = mongodb_connector.find_all_data({'operation_records.pre_op_record.operation_room': op_room})
        return patients
    except Exception as e:
        print(f"Error getting patient by operation room: {e}")
        raise e

@patient_query.field("getAllPatientsByOpDate")
def resolve_get_all_patients_by_op_date(root, info, op_date):
    """
    Resolver function for the getPatientByOperationDate query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        operation_date (str): The operation date to get the patient for.
    
    Returns:
        dict: A dictionary containing the patient data.
    """
    try:
        # Parse the date and create start and end date objects
        start_date_obj = parse(op_date)
        end_date_obj = start_date_obj + timedelta(days=1)
        # print(f"start_date_obj: {start_date_obj}")
        # print(f"end_date_obj: {end_date_obj}")

        patients = mongodb_connector.find_all_data({'operation_records.pre_op_record.operation_date': {
            '$gte': start_date_obj,
            '$lt': end_date_obj
        }})
        return patients
    except Exception as e:
        print(f"Error getting patient by operation date: {e}")
        raise e

@patient_query.field("getAllPatientsByOpType")
def resolve_get_all_patients_by_op_type(root, info, op_type):
    """
    Resolver function for the getAllPatientByOpType query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        op_type (str): The operation type to get the patient for.
    
    Returns:
        dict: A dictionary containing the patient data.
    """
    try:
        query = {'operation_records.pre_op_record.operation_type': op_type}
        # print(f"Executing query: {query}")  # Log the query
        patients = mongodb_connector.find_all_data(query)
        # print(f"Query result: {patients}")  # Log the result
        return patients
    except Exception as e:
        print(f"Error getting patient by operation type: {e}")
        raise e

@patient_query.field("getAllPatientsByAnesthesiaType")
def resolve_get_all_patients_by_anesthesia_type(root, info, anesthesia_type):
    """
    Resolver function for the getAllPatientByAnesthesiaType query.
    
    Args:
        root (None): The root object.
        info (None): The info object.
        anesthesia_type (str): The anesthesia type to get the patient for.
    
    Returns:
        dict: A dictionary containing the patient data.
    """
    try:
        query = {'operation_records.pre_op_record.anesthesia_typ': anesthesia_type}
        # print(f"Executing query: {query}")  # Log the query
        patients_cursor = mongodb_connector.find_all_data(query)
        patients = list(patients_cursor)  # Convert cursor to list to fetch all results
        # print(f"Query result: {patients}")  # Log the result
        return patients
    
    except Exception as e:
        print(f"Error getting patient by anesthesia type: {e}")
        raise e
    
