from flask import Flask
from graphene import ObjectType, String, Schema
from flask_graphql import GraphQLView

class Query(ObjectType):
    hello = String(description="A typical hello world field")

    def resolve_hello(self, info):
        return "world"

app = Flask(__name__)
schema = Schema(query=Query)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    app.run(host='192.168.29.120', port=5000, debug=True)
