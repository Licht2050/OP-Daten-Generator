
import asyncio
import aioredis
import logging
from indoor_environment_data_schema import IndoorEnvironmentDataValue

class GraphQLPublisher():
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.channel_name = 'indoor_environment_data_updated'
        self.redis = None

    async def initialize(self):
        self.redis = await aioredis.from_url('redis://localhost')

    async def close_redis(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
            
    async def process_data(self, processed_message):
        data = processed_message.raw_message
        value = data.get('value')
        self.logger.info(f"Received message in GraphQL Publisher: {processed_message.to_dict()}")
        
        num_subscribers = await self.redis.execute_command("PUBSUB", "NUMSUB", self.channel_name)
        num_subscribers = int(num_subscribers[1])
        print(f"Number of subscribers======================================: {num_subscribers}")
        if num_subscribers > 0:
            message = IndoorEnvironmentDataValue(**value)
            await self.redis.publish(self.channel_name, message.model_dump_json())
