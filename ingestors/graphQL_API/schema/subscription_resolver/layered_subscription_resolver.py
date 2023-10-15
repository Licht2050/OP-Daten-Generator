import os
import sys
import logging
from ariadne import ObjectType, SubscriptionType


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


from schema.subscription_resolver.redis_subscription import RedisSubscription
from schema.subscription_resolver.environment_data_sub_resolver import indoor_environment_data_updated_generator
from usable_functions.usable_functions import get_requested_fields, get_requested_subfields
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH



config_loader = ConfigLoader(CONFIG_FILE_PATH)

indoor_environment_channels = config_loader.load_config("publish_subscribe_channels")
print("indoor_environment_channels-------------------------:", indoor_environment_channels)
subscribe_channel = indoor_environment_channels.get("indoor_environment_channels").get("subscribe_channel")
unsbscribe_channel = indoor_environment_channels.get("indoor_environment_channels").get("unsubscribe_channel")
fields_channel = indoor_environment_channels.get("indoor_environment_channels").get("fields_channel")




op_environment_subscription = SubscriptionType()


@op_environment_subscription.source("subscribeByPatientId")
async def subscribe_by_patient_id_generator(obj, info, patientId):
    print("subscribe_by_patient_id_generator")
    
    update = {}
    requested_fields = get_requested_fields(info)
    print("requested_fields----------- ", requested_fields)
    if "opEnvironmentSubscription" in requested_fields:
        print("inside if")
        async for indoor_data in indoor_environment_data_updated_generator(obj, info, patientId):
            yield {
                "opEnvironment": {
                    "indoorEnvironment": indoor_data
                }
            }

    
    print("Update inside subscribeByPatientId:", update)
    # Hier können Sie später weitere Daten für andere Schichten hinzufügen.
    layered_data = {
        "opEnvironment": update.get("opEnvironment", {})
    }
    # yield layered_data
    
@op_environment_subscription.field("subscribeByPatientId")
def subscribe_by_patient_id_resolver(layered_data, info, patientId):
    print("subscribe_by_patient_id_resolver Field-----------")
    print("layered_data: ", layered_data)
    return layered_data

layered_patient_data_type = ObjectType("LayeredPatientData")

@layered_patient_data_type.field("opEnvironment")
def indoor_environment_resolver(layered_data, *_):
    print("indoor_environment_resolver")
    return layered_data["indoorEnvironment"]
