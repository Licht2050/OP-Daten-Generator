# data_publisher/data_publisher.py
class DataPublisher:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, subscriber):
        print(f"Adding subscriber {subscriber}")
        self.subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        self.subscribers.discard(subscriber)

    async def publish(self, data):
        print(f"Sending data to subscriber {data}")
        for subscriber in self.subscribers:
            print(f"Sending data to subscriber {subscriber}")
            subscriber.put_nowait(data)
