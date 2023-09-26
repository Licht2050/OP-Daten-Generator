import graphene
import asyncio

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


schema = graphene.Schema(query=Query, subscription=Subscription)