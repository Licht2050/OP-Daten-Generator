from rx.subject.subject import Subject
from .async_iterable_wrapper import AsyncIterableWrapper

# Create an instance of AsyncIterableWrapper
async_iterable_wrapper: AsyncIterableWrapper = AsyncIterableWrapper()

# Create a subject
indoor_environment_data_subject = Subject()

# Subscribe the async_iterable_wrapper to the subject
indoor_environment_data_subject.subscribe(async_iterable_wrapper.on_next)
