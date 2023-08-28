from cassandra.cluster import Cluster

class CassandraConnector:

    def __init__(self, nodes):
        self.cluster = Cluster(nodes)
        self.session = self.cluster.connect()

    def connect(self, keyspace, table_definition=None):
        self._ensure_keyspace(keyspace)
        self.session.set_keyspace(keyspace)
        if table_definition:
            self._ensure_table(table_definition)
        return self.session

    def _ensure_keyspace(self, keyspace):
        query = f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
        """
        self.session.execute(query)

    def _ensure_table(self, table_definition):
        self.session.execute(table_definition)

    def close(self):
        self.cluster.shutdown()
