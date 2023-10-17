
import json
import aioredis
import logging


class GraphQLPublisher():
    def __init__(self, subscribe_channel) -> None:
        self.logger = logging.getLogger(__name__)
        self.channel_name = subscribe_channel
        self.redis = None
       
            
    async def initialize(self):
        self.redis = await aioredis.from_url('redis://localhost')
       
    async def close_redis(self):

        if self.redis:
            await self.redis.close()
            self.redis = None
            

    async def process_data(self, processed_message):
        
        data, patient_id, value_data = self.extract_message_details(processed_message)
        # print(f"values===================: {value_data}")
        # self.logger.info(f"Received message in GraphQL Publisher: {processed_message.to_dict()}")
        # print(f"Received message in GraphQL Publisher: {processed_message.to_dict()}")
        channel_name_for_subscription = f"{self.channel_name}_{patient_id}"
        # print(f"channel_name_for_subscription: {channel_name_for_subscription}")
        num_subscribers = await self.redis.execute_command("PUBSUB", "NUMSUB", channel_name_for_subscription)
        num_subscribers = int(num_subscribers[1])
        # print(f"Number of subscribers======================================: {num_subscribers}")
        if num_subscribers > 0:
            # print(f"Publishing to channel: {channel_name_for_subscription}")
            # print(f"value data: {value_data}")
            await self.redis.publish(channel_name_for_subscription, json.dumps(value_data))
                                     
    
    def extract_message_details(self, processed_message):
        data = processed_message.to_dict()
        patient_id = processed_message.get_data("patient_id")
        value_data = data.get('value').model_dump(by_alias=False)
        return data,patient_id,value_data
