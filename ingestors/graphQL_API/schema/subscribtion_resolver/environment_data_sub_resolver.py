# subscription_resolver/environment_data_sub_resolver.py


import asyncio
import json
import os
import sys
from ariadne import SubscriptionType
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '../../../data_publisher')
])

import aioredis

from data_publisher_singleton import DataPublisherSingleton

data_publisher = DataPublisherSingleton.get_instance()

subscription = SubscriptionType()


async def subscribe_to_redis_channel(channel_name):
    print("Connecting to Redis")
    redis = await aioredis.from_url('redis://localhost')
    pubsub = redis.pubsub()
    print("Subscribing to channel")
    await pubsub.subscribe(channel_name)
    print("Subscribed to channel")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print("Received:", message)
                decoded_message = json.loads(message["data"].decode('utf-8'))
                print("Decoded message:", decoded_message)
                yield decoded_message
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print("Subscription cancelled, cleaning up")
    finally:
        await pubsub.unsubscribe('indoor_environment_data_updated')



@subscription.source("indoorEnvironmentDataUpdated")
async def indoor_environment_data_updated_generator(obj, info):
    print("indoor_environment_data_updated_generator")

    async for update in subscribe_to_redis_channel('indoor_environment_data_updated'):
        yield update




@subscription.field("indoorEnvironmentDataUpdated")
def indoor_environment_data_updated_resolver(update, info):
    print("indoor_environment_data_updated_resolver")
    return update

