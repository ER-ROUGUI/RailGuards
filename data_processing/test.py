from influxdb import InfluxDBClient

# InfluxDB Configuration
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = "sensor_data"

# Create InfluxDB client
client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)

# Select the database
client.switch_database(INFLUXDB_DATABASE)

# Write a test point
json_body = [
    {
        "measurement": "test_measurement",
        "tags": {
            "source": "python_test"
        },
        "fields": {
            "value": 42
        }
    }
]

try:
    client.write_points(json_body)
    print("Test point written successfully.")
except Exception as e:
    print(f"Failed to write to InfluxDB: {e}")
