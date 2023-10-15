from typing import Any
from ariadne import make_executable_schema, load_schema_from_path
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route
from ariadne.asgi.handlers import GraphQLWSHandler
import wsproto

# Import your query resolvers
from schema.query_resolvers.patient_resolvers import patient_query
from schema.schema import schema
import uuid


subscriptions = {}

# def on_connect(wbesocket, params: Any):
#     subscription_id = str(uuid.uuid4())
#     subscriptions[subscription_id] = wbesocket
#     wbesocket.scope['subscription_id'] = subscription_id
#     # print("Connected to websocket wit id: ", subscription_id)

# def on_disconnect(websocket):
#     try:
#         subscription_id = websocket.scope.get('subscription_id')
#         print("Subscription id: ", subscription_id)
#         print("Subscriptions: ", subscriptions)
#         if subscription_id in subscriptions:
            
#             print(f"[WS] Disconnected with id: {subscription_id}")
#             subscriptions.pop(subscription_id, None)
#         else:
#             print(f"[WS] No matching subscription for id: {subscription_id}")

#         if websocket.client_state == "disconnected":
#             print(f"[WS] WebSocket with id {subscription_id} is already disconnected.")
#             return

#     except wsproto.utilities.LocalProtocolError as e:
#         print(f"[WS] Protocol error: ")
#     except Exception as e:
#         print(f"[WS] Unexpected error: ")

# Create GraphQL app
graphql_app = GraphQL(
    schema=schema,
    debug=True,
    websocket_handler=GraphQLWSHandler(
        # on_connect=on_connect,
        # on_disconnect=on_disconnect,
    ),
)

# Create Starlette app and mount GraphQL app
app = Starlette(
    routes=[
        Route("/graphql/", graphql_app.handle_request, methods=["GET", "POST", "OPTIONS"]),
    ],
    debug=True,
)

app.mount("/", graphql_app)
