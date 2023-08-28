import os
import sys
from confluent_kafka import Consumer, KafkaError

sys.path.append(os.path.join(os.path.dirname(__file__), '../config'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../db_connectors'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../helper_classes_and_functions'))

from cassandra_connector import CassandraConnector
from config_loader import ConfigLoader

class KafkaToCassandra:

    def __init__(self, config_file_path):
        self.config_loader = ConfigLoader(config_file_path)
        self.CONFIG = self.config_loader.get_all_configs()

        self.KAFKA_CONFIG = {
            'bootstrap.servers': self.CONFIG['kafka']['bootstrap_servers'], 
            #'group.id': self.CONFIG['kafka']['group_id'],
            'auto.offset.reset': 'earliest'
        }

        self.consumer = self._init_consumer()
        self.cassandra_connector = CassandraConnector(self.CONFIG['cassandra']['nodes'])
        self.session = self.cassandra_connector.connect(self.CONFIG['cassandra']['keyspace'])
        self.middlewares = []

    def _init_consumer(self):
        return Consumer(self.KAFKA_CONFIG)

    def add_middleware(self, middleware_fn):
        self.middlewares.append(middleware_fn)

    def process_middlewares(self, message):
        for middleware in self.middlewares:
            message = middleware(message)
        return message

    def save_to_cassandra(self, message):
        message = self.process_middlewares(message)
        query = f"INSERT INTO {self.CONFIG['cassandra']['table']} (...) VALUES (...)"
        self.session.execute(query, (message.value['field1'], ...))

    def consume_and_store(self):
        while True:
            message = self.consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    print(f"Reached end of partition {message.partition()}")
                else:
                    print(f"Error while consuming message: {message.error()}")
            else:
                self.save_to_cassandra(message)

    def close_connections(self):
        self.consumer.close()
        self.cassandra_connector.close()

    def run(self):
        try:
            self.consumer.subscribe([self.CONFIG['kafka']['topic']])
            self.consume_and_store()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close_connections()

if __name__ == '__main__':
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
    TABLE_DEFINITION = """
        CREATE TABLE IF NOT EXISTS vital_params (
            Patient_ID UUID,
            timestamp TIMESTAMP,
            source TEXT,
            oxygen_saturation INT,
            systolic INT,
            diastolic INT,
            etco2 INT,
            bispectral_index INT,
            PRIMARY KEY (Patient_ID, timestamp)
        )
    """

    connector = KafkaToCassandra(CONFIG_FILE_PATH)
    connector.cassandra_connector.connect('my_keyspace', TABLE_DEFINITION)
    
    # Beispiel-Middleware 
    def example_middleware(message):
        #
        return message

    connector.add_middleware(example_middleware)
    connector.run()
