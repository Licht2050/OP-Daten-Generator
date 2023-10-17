# subscription_resolver/vital_params_resolver.py


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
print("vital_params_channels-------------------------:", channels)

bispectral_index_channel = channels.get("bispectral_index").get("subscribe_channel")
blood_pressure_channel = channels.get("blood_pressure").get("subscribe_channel")
heart_rate_channel = channels.get("heart_rate").get("subscribe_channel")
oxygen_saturation_channel = channels.get("oxygen_saturation").get("subscribe_channel")
etco2 = channels.get("etco2").get("subscribe_channel")


subscription = SubscriptionType()



@subscription.source("bispectralIndexByPid")
async def bispectral_index_by_pid_generator(obj, info, patientId):
    print("bispectral_index_by_pid_generator")

    requested_fields = get_requested_fields(info)

    channel_name = f"{bispectral_index_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        yield update


@subscription.source("bloodPressureByPid")
async def blood_pressure_by_pid_generator(obj, info, patientId):
    print("blood_pressure_by_pid_generator")

    requested_fields = get_requested_fields(info)

    channel_name = f"{blood_pressure_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        yield update


@subscription.source("heartRateByPid")
async def heart_rate_by_pid_generator(obj, info, patientId):
    print("heart_rate_by_pid_generator")

    requested_fields = get_requested_fields(info)

    channel_name = f"{heart_rate_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        yield update


@subscription.source("oxygenSaturationByPid")
async def oxygen_saturation_by_pid_generator(obj, info, patientId):
    print("oxygen_saturation_by_pid_generator")

    requested_fields = get_requested_fields(info)

    channel_name = f"{oxygen_saturation_channel}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        yield update


@subscription.source("etco2ByPid")
async def etco2_by_pid_generator(obj, info, patientId):
    print("etco2_by_pid_generator")

    requested_fields = get_requested_fields(info)

    channel_name = f"{etco2}_{patientId}"
    # print("channel_name: ", channel_name)
   
    redis_sub = RedisSubscription(channel_name, requested_fields)
    await redis_sub.connect_to_redis()
    
    async for update in redis_sub.get_filtered_messages():
        yield update



@subscription.field("bispectralIndexByPid")
def bispectral_index_by_pid_resolver(update, info, patientId):
    return update


@subscription.field("bloodPressureByPid")
def blood_pressure_by_pid_resolver(update, info, patientId):
    return update


@subscription.field("heartRateByPid")
def heart_rate_by_pid_resolver(update, info, patientId):
    return update


@subscription.field("oxygenSaturationByPid")
def oxygen_saturation_by_pid_resolver(update, info, patientId):
    return update


@subscription.field("etco2ByPid")
def etco2_by_pid_resolver(update, info, patientId):
    return update


