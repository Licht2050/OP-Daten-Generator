from influxdb import InfluxDBClient

# Connect to the InfluxDB instance
client = InfluxDBClient(host='localhost', port=8086, database='medical_data')

# Fetch the list of all measurements
measurements = client.query('SHOW MEASUREMENTS')
measurements_list = list(measurements.get_points())

# Drop each measurement
for measurement in measurements_list:
    client.query(f'DROP MEASUREMENT "{measurement["name"]}"')

print("All measurements have been deleted.")
