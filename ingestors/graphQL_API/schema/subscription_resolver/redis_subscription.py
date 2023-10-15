import asyncio
import json
import aioredis


class RedisSubscription:
    
    def __init__(self, channel_name, requested_fields=None):
        self.channel_name = channel_name
        self.requested_fields = requested_fields or []

    async def connect_to_redis(self):
        print("Connecting to Redis")
        self.redis = await aioredis.from_url('redis://localhost')
        self.pubsub = self.redis.pubsub()
        print("Subscribing to channel")
        await self.pubsub.subscribe(self.channel_name)
        print(f"Subscribed to channel: {self.channel_name}")

    async def get_filtered_messages(self):
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    
                    decoded_message = json.loads(message["data"].decode('utf-8'))

                    print(f"Received message===========: {decoded_message}")
                    print(f"Requested fields: {self.requested_fields}")
                    filtered_message = {key: decoded_message[key] for key in self.requested_fields if key in decoded_message}
                    print(f"Filtered message: {filtered_message}")
                    yield filtered_message
        except asyncio.CancelledError:
            print("Subscription cancelled, cleaning up")
        finally:
            await self.pubsub.unsubscribe(self.channel_name)