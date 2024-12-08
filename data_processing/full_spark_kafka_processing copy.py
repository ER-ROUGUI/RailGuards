from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, FloatType, BooleanType, TimestampType
from influxdb import InfluxDBClient
from datetime import datetime
from pyspark.sql.functions import current_timestamp

# InfluxDB 1.x configuration
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086  
INFLUXDB_DATABASE = "sensor_data"  # InfluxDB 1.x database name

# Create InfluxDB client (no need for token and org in InfluxDB 1.x)
influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
# Select the database
influx_client.switch_database(INFLUXDB_DATABASE)

def write_to_influxdb(batch_df):
    """
    Write cleaned data from Spark batch to InfluxDB 1.x.
    :param batch_df: Spark DataFrame containing cleaned data from the batch.
    """
    try:
        # Convert each row to a format suitable for InfluxDB
        data = []
        for row in batch_df.collect():
            # Check if timestamp is null
            if row["timestamp"] is None:
                print("Timestamp is None, skipping this row.")
                continue
            
            # Ensure timestamp is in the correct format
            # timestamp = int(row["timestamp"]) * 1000000000  # Convert to nanoseconds
            timestamp = int(row["timestamp"].timestamp()) * 1000000000
            # Construct data in the InfluxDB 1.x format
            data.append(
                {
                    "measurement": "cleaned_sensor_data",  # This is the measurement name
                    "tags": {"source": "spark"},
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
            )

        # Write data to InfluxDB in batch
        if data:
            influx_client.write_points(data)
            print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write to InfluxDB: {e}")

# Define the schema for combined sensor data
schema = StructType() \
    .add("timestamp", TimestampType()) \
    .add("pressure", FloatType()) \
    .add("oil_temperature", FloatType()) \
    .add("motor_current", FloatType()) \
    .add("air_temperature", FloatType()) \
    .add("humidity", FloatType()) \
    .add("vibration", FloatType()) \
    .add("air_pressure", FloatType()) \
    .add("valve_intake", BooleanType()) \
    .add("valve_outlet", BooleanType()) \
    .add("compressor_status", BooleanType()) \
    .add("filter_status", BooleanType()) \
    .add("safety_switch", BooleanType()) \
    .add("overload_protection", BooleanType()) \
    .add("emergency_stop", BooleanType()) \
    .add("door_sensor", BooleanType())

def main():
    # Create SparkSession
    spark = SparkSession.builder \
        .appName("Simple Sensor Data Cleaning") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Read data from Kafka
    raw_data = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "fulldata") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse the JSON data
    parsed_data = raw_data.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Ensure the timestamp is not null, or replace it with the current timestamp
    parsed_data = parsed_data.withColumn(
        "timestamp", when(col("timestamp").isNull(), current_timestamp()).otherwise(col("timestamp"))
    )
    
    # Filter invalid data based on defined ranges
    cleaned_data = parsed_data.filter(
        (col("pressure").between(1.0, 10.0)) &
        (col("oil_temperature").between(30.0, 90.0)) &
        (col("motor_current").between(0.5, 5.0)) &
        (col("air_temperature").between(15.0, 40.0)) &
        (col("humidity").between(30.0, 90.0)) &
        (col("vibration").between(0.1, 2.0)) &
        (col("air_pressure").between(1.0, 10.0))
    )

    # Write the cleaned data to InfluxDB using foreachBatch
    cleaned_data.writeStream \
        .foreachBatch(lambda batch_df, batch_id: write_to_influxdb(batch_df)) \
        .start()
    
    # Write cleaned data to a new Kafka topic
    query = cleaned_data.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "cleaned_sensor_data") \
        .option("checkpointLocation", "/tmp/spark_simple_clean_checkpoint") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
