from influxdb_client import InfluxDBClient, Point, WriteOptions
from datetime import datetime, timezone
import json

# InfluxDB configuration (for InfluxDB 2.x)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "your_influxdb_token"  # Replace with your token
INFLUXDB_ORG = "your_org"  # Replace with your org name
INFLUXDB_BUCKET = "smart_sensors"  # Replace with your InfluxDB bucket name

# Create InfluxDB client
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

def write_to_influxdb(row):
    """
    Write cleaned data from Spark to InfluxDB.
    :param row: Row of cleaned data from Spark DataFrame.
    """
    try:
        # Validate that timestamp is not None
        if row["timestamp"] is None:
            raise ValueError("Invalid timestamp: None")

        # Ensure timestamp is in the correct format
        timestamp = datetime.fromtimestamp(row["timestamp"], timezone.utc).isoformat()

        # Construct data in the InfluxDB 2.x format
        data = [
            {
                "measurement": "cleaned_sensor_data",
                "tags": {
                    "source": "spark"
                },
                "fields": {
                    "pressure": row["pressure"],
                    "oil_temperature": row["oil_temperature"],
                    "motor_current": row["motor_current"],
                    "air_temperature": row["air_temperature"],
                    "humidity": row["humidity"],
                    "vibration": row["vibration"],
                    "air_pressure": row["air_pressure"]
                },
                "time": timestamp
            }
        ]

        # Write data to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=data)
        print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write to InfluxDB: {e}")

