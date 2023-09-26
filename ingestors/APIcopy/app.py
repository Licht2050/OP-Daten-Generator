import asyncio
import logging
from flask import Flask, render_template
from schema.schema import schema  # Ensure schema is correctly imported
from graphql_server.flask import GraphQLView
from flask_socketio import SocketIO, emit
from graphql import ExecutionResult, parse

app = Flask(__name__)
# socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins='*')

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,
        context={'logger': logging.getLogger()}
    )
)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('graphql_subscription')
def handle_graphql_subscription(json):
    query = json.get('query')

    def background_task():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_query_execution(query))  # Pass the query string directly

    socketio.start_background_task(background_task)


async def async_query_execution(query):
    subscription = None
    try:
        subscription = await schema.subscribe(query=query)
    except Exception as e:
        print(f"Error in subscribing: {e}")
    # Check if subscription setup was successful
    if isinstance(subscription, ExecutionResult):
        print(f"Subscription setup failed: {subscription.errors}")
        return

    print(f"Subscription result: {subscription}")  
    
    async for result in subscription:
        data = result.data
        print(data)
        emit('graphql_subscription', data)




if __name__ == '__main__':
    app.logger.setLevel(logging.INFO)
    socketio.run(app, host='192.168.29.120', port=5000, debug=True)