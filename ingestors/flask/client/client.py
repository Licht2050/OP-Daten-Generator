import asyncio
import json
import websockets.client
from websockets.exceptions import ConnectionClosed

async def subscribe():
    uri = "ws://192.168.29.120:5000/graphql-test"
    test_token = "mySuperSecretKey123"
    #connection init
    connection_init_mutation = {
        "type": "connection_init",
        "payload": {
            "authToken": f"Bearer {test_token}"
        }
    }


    subscription_query = {
        "type": "start",
        "id": "1",
        "payload": {
            "query": "subscription { time }",
            "variables": {}
        }
    }

    async with websockets.client.connect(uri) as websocket:
        await websocket.send(json.dumps(connection_init_mutation))
        print("> Sent connection_init")

        await websocket.recv()
        print("< Received connection_ack")

        await websocket.send(json.dumps(subscription_query))
        print(f"> Sent subscription query: {subscription_query}")



        try:
            while True:
                response = await websocket.recv()
                print(f"< Received: {response}")
        except ConnectionClosed as e:
            print(f"Connection closed: {e}")

asyncio.run(subscribe())
