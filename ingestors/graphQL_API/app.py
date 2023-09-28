from ariadne import make_executable_schema, load_schema_from_path
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route
from ariadne.asgi.handlers import GraphQLWSHandler

# Import your query resolvers
from schema.query_resolvers.patient_resolvers import patient_query
from schema.schema import schema



# Create GraphQL app
graphql_app = GraphQL(
    schema=schema,
    debug=True,
    websocket_handler=GraphQLWSHandler(),
)

# Create Starlette app and mount GraphQL app
app = Starlette(
    routes=[
        Route("/graphql/", graphql_app.handle_request, methods=["GET", "POST", "OPTIONS"]),
    ],
    debug=True,
)

app.mount("/", graphql_app)
