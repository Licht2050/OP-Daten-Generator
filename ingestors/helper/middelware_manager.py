from typing import Any, Callable
from processed_message import ProcessedMessage
import asyncio

class MiddlewareManager:
    def __init__(self):
        self.middlewares = []

    def add_middleware(self, middleware_fn: Callable) -> None:
        """Add middleware function."""
        self.middlewares.append(middleware_fn)

    async def process_middlewares(self, message: Any) -> Any:
        """Process middleware functions on message."""
        processed_message = ProcessedMessage(message)
        
        for middleware in self.middlewares:
            if asyncio.iscoroutinefunction(middleware):
                await middleware(processed_message)

            else:
                middleware(processed_message)
            if processed_message is None:
                print(f"Warning: processed_message is None after {middleware.__name__}")
        return processed_message
