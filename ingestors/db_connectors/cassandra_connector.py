import logging
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

logging.basicConfig(level=logging.INFO)

class CassandraConnector:

    def __init__(self, nodes):
        self.cluster = Cluster(
            nodes,
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
            protocol_version=5
        )
        self.session = self.cluster.connect()

    def connect(self, keyspace, table_definition=None):
        self._ensure_keyspace(keyspace)
        print(f"Connecting to keyspace {keyspace}")
        self.session.set_keyspace(keyspace)
        if table_definition:
            self._ensure_table(table_definition)
        return self.session

    def _ensure_keyspace(self, keyspace):
        query = f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
        """
        try:
            print("Trying to create keyspace...")
            self.session.execute(query)
            print(f"Keyspace {keyspace} ensured.")
        except Exception as e:
            logging.error(f"Could not create keyspace {keyspace}: {e}")
            print(f"Could not create keyspace {keyspace}: {e}")

    def _ensure_table(self, table_definition):
            try:
                print(f"Executing: {table_definition}")
                self.session.execute(table_definition)
            except Exception as e:
                logging.error(f"Could not execute table definition: {e}")
                print(f"Could not execute table definition: {e}")


    def close(self):
        self.cluster.shutdown()
