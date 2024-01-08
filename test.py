from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime
import matplotlib.pyplot as plt
from cassandra.policies import DCAwareRoundRobinPolicy


cluster = Cluster(
            ["127.0.0.1"],
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
            protocol_version=5
        )

session = cluster.connect('medical_data')

# Query the data
query = "SELECT timestamp, estimated_time FROM heart_rate;"

rows = session.execute(query)


# Calculate deviations
deviations = []
for row in rows:
    # print(row)
    timestamp = row.timestamp
    estimated_time = row.estimated_time
    deviation = (estimated_time - timestamp).total_seconds() * 1000
    deviations.append(deviation)
    # print(f"Timestamp: {timestamp}, Estimated time: {estimated_time}, Deviation: {deviation}")



# Visualize the deviations
plt.plot(deviations)
plt.axhline(0, color='grey', linewidth=0.8)
plt.xlabel('Record Number')
plt.ylabel('Deviation (milliseconds)')
plt.title('Deviation Between Timestamp and Estimated Time')
plt.show()

plt.savefig('deviations_plot.png', dpi=300)

# Close the connection
cluster.shutdown()

