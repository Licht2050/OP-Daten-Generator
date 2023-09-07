from typing import Any, Callable
from processed_message import ProcessedMessage


class MiddlewareManager:
    def __init__(self):
        self.middlewares = []

    def add_middleware(self, middleware_fn: Callable) -> None:
        """Add middleware function."""
        self.middlewares.append(middleware_fn)

    def process_middlewares(self, message: Any) -> Any:
        """Process middleware functions on message."""
        processed_message = ProcessedMessage(message)
        for middleware in self.middlewares:
            middleware(processed_message)
        return processed_message
