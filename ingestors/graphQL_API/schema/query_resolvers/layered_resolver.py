import os
import sys
import logging
from ariadne import ObjectType
import uuid
from cassandra.query import named_tuple_factory


from usable_functions.usable_functions import calculate_average, calculate_time_range, get_requested_fields, str_to_datetime
from schema.query_resolvers.vital_params_resolvers import get_requested_subfields, resolve_get_vital_params_by_date
from schema.query_resolvers.patient_resolvers import resolve_get_patient_by_id
from schema.query_resolvers.op_details_resolvers import resolve_get_op_details_by_id
from schema.query_resolvers.environment_resolvers import resolve_get_op_environment_data_by_date_and_pid
from schema.query_resolvers.external_factors_resolver import resolve_get_outdoor_environment_by_time_and_pid

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../db_connectors'),
    os.path.join(os.path.dirname(__file__), '../../../schema/cql'),
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../helper'))
])


# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

vital_params_query = ObjectType("VitalParamsQuery")



@vital_params_query.field("getHeartRateByDate")
def resolve_heart_by_date(root, info, patientId, timestamp, secondsRange):

    requested_field_names = get_requested_fields(info)
    print(requested_field_names)

    result = {}
    
    if "vitalParams" in requested_field_names:
        vital_params = resolve_get_vital_params_by_date(root, info, patientId, timestamp, secondsRange)
        result["vitalParams"] = vital_params["vitalParams"]
        # print("vitParams in result: "+ str(result["vitalParams"]))
    if "patientProfile" in requested_field_names:
        patient = resolve_get_patient_by_id(root, info, patientId)
        result["patientProfile"] = patient
    if "opDetails" in requested_field_names:
        requested_fields = get_requested_subfields(info.field_nodes[0], "opDetails")
        # print(requested_fields)
        op_details = resolve_get_op_details_by_id(root, info, patientId, requested_fields)
        result["opDetails"] = op_details
        print("opDetails in result: "+ str(result.get("opDetails").get("pre_op_record").get("operation_room")))

    if "opEnvironment" in requested_field_names:
        print("opEnvironment in requested_field_names")
        op_environment = resolve_get_op_environment_data_by_date_and_pid(root, info, patientId, timestamp, secondsRange)

        # print("opEnvironment: "+ str(op_environment))
        result["opEnvironment"] = op_environment
    
    if "externalFactros" in requested_field_names:
        print("externalFactors in requested_field_names")
        external_factors = resolve_get_outdoor_environment_by_time_and_pid(root, info, patientId, timestamp, secondsRange)
        print("externalFactors: "+ str(external_factors))
        result["externalFactros"] = external_factors
    # print("result: "+ str(result))
    return result






