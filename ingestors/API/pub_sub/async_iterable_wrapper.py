import asyncio
from typing import Any, AsyncIterator
import logging

class AsyncIterableWrapper:
    def __init__(self)  -> None:
        self._queue = asyncio.Queue()

    def __aiter__(self)   :
        logging.info("AsyncIterableWrapper: __aiter__ called")
        return self

    
    async def __anext__(self)   -> Any:
        logging.info("AsyncIterableWrapper: __anext__ called")
        logging.info(f"AsyncIterableWrapper: __anext__ before Queue:")
        data = await self._queue.get()
        logging.info(f"AsyncIterableWrapper: __anext__ after Queue:")
        if data is None:  
            raise StopAsyncIteration
        return data

    def on_next(self, value)    -> None:
        logging.info(f"AsyncIterableWrapper: on_next called with value: {value}")
        if self._queue is not None:
            self._queue.put_nowait(value)
        logging.info(f"Data received in async iterable wrapper: {value}")


    
