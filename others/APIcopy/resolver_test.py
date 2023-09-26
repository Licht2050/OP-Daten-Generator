import asyncio
import logging
from schema.schema import IndoorEnvironmentDataSubscription

async def main():
    # Call the resolver function directly
    async_iterable = await IndoorEnvironmentDataSubscription.resolve_indoor_environment_data_update(None, None, "test_room")
    
    if async_iterable is not None:
        # Iterate over the async iterable to get the data
        async for data in async_iterable:
            print(data)
    else:
        print("Resolver returned None")

# Run the main function
asyncio.run(main())