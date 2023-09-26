import json
from ariadne import SubscriptionType, make_executable_schema, MutationType
from ariadne.asgi import GraphQL
from broadcaster import Broadcast
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from ariadne.asgi.handlers import GraphQLWSHandler




# Initialize broadcaster with in-memory channel
broadcast = Broadcast("memory://")

type_defs = """
    type Query {
        _unused: Boolean
    }

    type Mutation {
        increaseCounter: Boolean
    }

    type Subscription {
        counter: Int!
    }
"""

mutation = MutationType()

# Initialize the counter
counter = 0

@mutation.field("increaseCounter")
async def resolve_increase_counter(*_, **__):
    global counter
    print("Increase counter mutation called")

    # Increase the counter and broadcast the new count
    counter += 1
    await broadcast.publish(channel="counter_channel", message=json.dumps(counter))
    print(f"Counter increased to {counter}")
    return True

subscription = SubscriptionType()

@subscription.source("counter")
async def counter_source(_, info):
    print("Subscription started")
    async with broadcast.subscribe(channel="counter_channel") as subscriber:
        try:
            async for event in subscriber:
                print(f"Sending message: {event}")
                yield json.loads(event.message)
        except Exception as e:
            print(f"Error in subscription: {e}")
        finally:
            print("Subscription ended")

@subscription.field("counter")
def counter_resolver(count, _):
    print(f"Resolving counter: {count}")
    return count




schema = make_executable_schema(type_defs, mutation, subscription)

graphql_app = GraphQL(
    schema=schema, 
    debug=True,
    websocket_handler=GraphQLWSHandler(),
    # websocket_handler=GraphQLTransportWSHandler(),
)

app = Starlette(
    routes=[
        Route("/graphql/", graphql_app.handle_request, methods=["GET", "POST", "OPTIONS"]),
        WebSocketRoute("/graphql/", graphql_app.handle_websocket),
    ],
    debug=True, on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect])
app.mount("/", graphql_app)
