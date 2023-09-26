import asyncio
from datetime import datetime
import strawberry
from typing import AsyncGenerator
import jwt
import logging

logger = logging.getLogger(__name__)

# Secret Key for encoding and decoding JWT
SECRET_KEY = "mySuperSecretKey123!"

# Test user data
users = {
    "test_user": "test_password"
}


@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, username: str, password: str) -> str:
        # Validate the username and password against the users dictionary
        if users.get(username) == password:
            # If the credentials are valid, return a JWT token
            token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
            return token
        else:
            # If the credentials are invalid, return an error
            raise Exception("Invalid credentials")



@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, World!"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def time(self, info) -> str:
        logger.debug("Subscription resolver: time")
        connection_params = info.context.get("connection_params")
        token = connection_params.get("authToken")
        logger.debug(f"Received token: {token}")

        try:
            # Validate the token
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.DecodeError:
            # If the token is invalid, reject the connection
            raise Exception("Invalid token")
        # If the token is valid, return the subscription data
        return "current time: " + str(datetime.now().time())

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)


