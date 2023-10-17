
import asyncio
import json
import os
import sys
from typing import Dict, Any

import aioredis
import copy

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../helper'))

from base import Base


class GraphQLVitalParamPub(Base):
    def __init__(self, vital_param_channels: Dict[str, Any]) -> None:
        super().__init__()
        self._setup_logging()
        self.vital_param_channels = vital_param_channels
        self.event_loop = asyncio.new_event_loop()


    async def initialize(self):
        try:
            self.redis = await aioredis.from_url('redis://localhost')
        except Exception as e:
            self.logger.error(f"Error initializing redis: {e}")
            raise   
    async def close(self):

        if self.redis:
            await self.redis.close()
            self.redis = None
        

    def process_data(self, processed_message):
        # print("Processing data in GraphQL Publisher")
        message_dict = processed_message.to_dict()
        # print(f"data: {message_dict}")

        source, patient_id, value_data = self.extract_message_details(message_dict)
        if not source in self.vital_param_channels:
            return

        channel_name = self.vital_param_channels[source].get('subscribe_channel')
        if not channel_name:
            return

        # print(f"values===================: {value_data}")
        channel_name_for_subscription = f"{channel_name}_{patient_id}"
        num_subscribers = self.event_loop.run_until_complete(self.get_num_subscribers(channel_name_for_subscription))
        # print(f"Number of subscribers======================================: {num_subscribers}")
        if num_subscribers > 0:
            # print(f"Publishing to channel: {channel_name_for_subscription}")
            # print(f"value data: {value_data}")
            # Publish data to the channel asynchronously
            self.event_loop.run_until_complete(self.publish_to_channel(channel_name_for_subscription, json.dumps(value_data)))

    

    async def publish_to_channel(self, channel_name, message):
        if self.redis:
            await self.redis.publish(channel_name, message)

    async def get_num_subscribers(self, channel_name):
        if self.redis:
            num_subscribers = await self.redis.execute_command("PUBSUB", "NUMSUB", channel_name)
            return int(num_subscribers[1])
        return 0


    def extract_message_details(self, processed_message):
        source = processed_message.get('source')
        status = processed_message.get('status')
        patient_id = processed_message.get('value').get("Patient_ID")
        value_data = processed_message.get('value')
        value_data_cpy = copy.deepcopy(value_data)
        value_data_cpy["patient_id"] = value_data_cpy.pop("Patient_ID")
        value_data_cpy["status"] = status
        return source, patient_id, value_data_cpy
