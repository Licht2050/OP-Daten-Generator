
from flask import Flask
from flask_socketio import SocketIO, emit
import graphene
import asyncio
import json
from graphql_server.flask import GraphQLView

class Query(graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(root, info):
        return "Hello, World!"

class Subscription(graphene.ObjectType):
    count_seconds = graphene.Int()
    
    async def resolve_count_seconds(root, info):
        for i in range(1, 11):
            yield i
            await asyncio.sleep(1)

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, cors_allowed_origins="*")
schema = graphene.Schema(query=Query, subscription=Subscription)

app.add_url_rule(
    '/graphql-api', 
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

@socketio.on('graphql-api')
def handle_message(json_data):
    query = json_data.get('query')
    result = schema.execute(query, context_value={'socketio': socketio})
    if hasattr(result, 'subscribe'):
        async def generator():
            async for item in result.subscribe(result, None):
                yield json.dumps(item.data)
        socketio.start_background_task(target=generator)

if __name__ == '__main__':
    socketio.run(app, host='192.168.29.120', port=5000,  debug=True)
