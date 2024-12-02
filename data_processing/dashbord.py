from influxdb import InfluxDBClient
from datetime import datetime

# InfluxDB 1.x configuration
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086  
INFLUXDB_DATABASE = "sensor_data" # InfluxDB 1.x database name

# Create InfluxDB client (no need for token and org in InfluxDB 1.x)
influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
# Select the database
influx_client.switch_database(INFLUXDB_DATABASE)
def write_to_influxdb(row):
    """
    Write cleaned data from Spark to InfluxDB 1.x.
    :param row: Row of cleaned data from Spark DataFrame.
    """
    try:
        # Debugging: Check if timestamp is null
        if row["timestamp"] is None:
            print("Timestamp is None, skipping this row.")
            return
        
        # Ensure timestamp is in the correct format
        timestamp = datetime.utcfromtimestamp(row["timestamp"]).isoformat() + "Z"

        # Construct data in the InfluxDB 1.x format
        data = [
                    {
                        "measurement": "cleaned_sensor_data",  # This is the measurement name
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
        influx_client.write_points(data)
        print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write to InfluxDB: {e}")

# Example usage (replace with actual Spark DataFrame row structure during integration)
if __name__ == "__main__":

    sample_row = {
        "timestamp": 1701523200.0,  # Unix timestamp
        "pressure": 8.5,
        "oil_temperature": 65.0,
        "motor_current": 2.1,
        "air_temperature": 25.7,
        "humidity": 50.2,
        "vibration": 1.0,
        "air_pressure": 5.3
    }
    write_to_influxdb(sample_row)