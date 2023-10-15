# subscription_resolver/environment_data_sub_resolver.py


import asyncio
import json
import os
import sys
from ariadne import ObjectType, SubscriptionType

from schema.subscription_resolver.redis_subscription import RedisSubscription

sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../config'),
    os.path.join(os.path.dirname(__file__), '../../../../helper_classes_and_functions'),
    os.path.join(os.path.dirname(__file__), '../../../data_publisher')
])



from usable_functions.usable_functions import get_requested_fields, get_requested_subfields
from config_loader import ConfigLoader
from paths_config import CONFIG_FILE_PATH



config_loader = ConfigLoader(CONFIG_FILE_PATH)

channels = config_loader.load_config("publish_subscribe_channels")
print("indoor_environment_channels-------------------------:", channels)
indoor_environment_channel = channels.get("indoor_environment_channels").get("subscribe_channel")
staff_communication_channel = channels.get("staff_communication").get("subscribe_channel")
entry_exit_events_channel = channels.get("entry_exit_events").get("subscribe_channel")





subscription = SubscriptionType()






@subscription.source("indoorEnvironmentByPid")
async def indoor_environment_by_pid_generator(obj, info, patientId):
    print("indoor_environment_data_updated_generator")

    requested_fields = get_requested_fields(info)
    # requested_fields = get_requested_subfields(info.field_nodes[0], "opEnvironment")
    # print("requested_fields++++++++++++++: ", requested_fields)
    # requested_fields = requested_fields.get("indoorEnvironment")

    channel_name = f"{indoor_environment_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        # print("Update inside indoor_environment_data_updated_generator:", update)
        yield update


@subscription.field("indoorEnvironmentByPid")
def indoor_environment_by_pid_resolver(update, info, patientId):
    # print("indoor_environment_data_updated_resolver")
    return update



@subscription.source("staffCommunicationByPid")
async def staff_communication_by_pid_generator(obj, info, patientId):
    print("staff_communication_by_pid_generator")

    requested_fields = get_requested_fields(info)
    print("requested_fields++++++++++++++: ", requested_fields)
    channel_name = f"{staff_communication_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        # print("Update inside indoor_environment_data_updated_generator:", update)
        yield update


@subscription.field("staffCommunicationByPid")
def staff_communication_by_pid_resolver(update, info, patientId):
    # print("indoor_environment_data_updated_resolver")
    return update



@subscription.source("entryExitEventByPid")
async def entry_exit_event_by_pid_generator(obj, info, patientId):
    print("entry_exit_event_by_pid_generator")

    requested_fields = get_requested_fields(info)
    print("requested_fields++++++++++++++: ", requested_fields)
    channel_name = f"{entry_exit_events_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        # print("Update inside indoor_environment_data_updated_generator:", update)
        yield update