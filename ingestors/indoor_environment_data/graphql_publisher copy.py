
import asyncio
import json
import threading
import aioredis
import logging
from indoor_environment_data_schema import IndoorEnvironmentDataValue
from pydantic import BaseModel


class GraphQLPublisher():
    def __init__(self, subscribe_channel, field_channel) -> None:
        self.logger = logging.getLogger(__name__)
        self.channel_name = subscribe_channel
        self.redis = None
        self.requested_fields_channel = field_channel
        # self.requested_data = {}
        # self.data_lock = threading.Lock()

    # def listen_for_requested_fields(self):
    #     try:
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #         pubsub = self.redis.pubsub()
    #         loop.run_until_complete(pubsub.subscribe(self.requested_fields_channel))
    #         print(f"Subscribed to channel: {self.requested_fields_channel}")
    #         while True:
    #             message = loop.run_until_complete(pubsub.get_message(ignore_subscribe_messages=True))
    #             if message:
    #                 decoded_message = json.loads(message["data"].decode('utf-8'))
    #                 subscription_id = decoded_message.get("subscription_id")
    #                 fields = decoded_message.get("requested_fields")
    #                 patient_id = decoded_message.get("patientId")

    #                 with self.data_lock:
    #                     self.requested_data[subscription_id] = {"patient_id": patient_id, "fields": fields}

    #                 self.logger.info(f"Updated requested fields: {self.requested_data}")
    #     except Exception as e:
    #         print(f"Error in listen_for_requested_fields: {e}")



            
    async def initialize(self):
        self.redis = await aioredis.from_url('redis://localhost')
        # threading.Thread(target=self.listen_for_requested_fields, daemon=True).start()
        # threading.Thread(target=self.listen_for_unsubscribes, daemon=True).start()


    async def close_redis(self):

        if self.redis:
            await self.redis.close()
            self.redis = None
            


    # async def process_data(self, processed_message):
        
    #     data, patient_id, value_data = self.extract_message_details(processed_message)
        
    #     for subscription_id, data in self.requested_data.items():
    #         print(f"Subscription id: {subscription_id}")
    #         print(f"patient id: {patient_id} and data patient id: {data['patient_id']}")
    #         if data["patient_id"] == patient_id:
    #             fields = data.get("fields")
    #             filtered_value = {k: value_data[k] for k in fields if k in value_data}
    #             channel_name_for_subscription = f"{self.channel_name}_{subscription_id}"
    #             print(f"Filtered value: {filtered_value}, requested fields: {self.requested_data}")

    #             # message = IndoorEnvironmentDataValue(**filtered_value)
    #             await self.redis.publish(channel_name_for_subscription, json.dumps(filtered_value))



    async def process_data(self, processed_message):
        
        data, patient_id, value_data = self.extract_message_details(processed_message)
        print(f"values===================: {value_data}")
        # self.logger.info(f"Received message in GraphQL Publisher: {processed_message.to_dict()}")
        channel_name_for_subscription = f"{self.channel_name}_{patient_id}"
        num_subscribers = await self.redis.execute_command("PUBSUB", "NUMSUB", channel_name_for_subscription)
        num_subscribers = int(num_subscribers[1])
        print(f"Number of subscribers======================================: {num_subscribers}")
        if num_subscribers > 0:
            print(f"Publishing to channel: {channel_name_for_subscription}")
            # message = IndoorEnvironmentDataValue(**value_data)
            print(f"value data: {value_data}")
            await self.redis.publish(channel_name_for_subscription, json.dumps(value_data))
                                     
    
    def extract_message_details(self, processed_message):
        data = processed_message.to_dict()
        patient_id = processed_message.get_data("patient_id")
        value_data = data.get('value').model_dump(by_alias=False)
        return data,patient_id,value_data
