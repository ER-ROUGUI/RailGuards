from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, current_timestamp, lit
from pyspark.sql.types import StructType, FloatType, TimestampType, IntegerType, StringType
from influxdb import InfluxDBClient
from functools import reduce
from kafka import KafkaConsumer
import json
from threading import Thread

# InfluxDB configuration
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = "sensor_data"

# Create InfluxDB client
influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
influx_client.switch_database(INFLUXDB_DATABASE)

# Kafka Consumer for anomaly data
anomaly_consumer = KafkaConsumer(
    'future_anomaly_predictions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Cache for maintenance_flag
anomaly_cache = {}

# Function to fetch anomalies from Kafka and cache them
def fetch_anomalies():
    """Fetch anomalies from Kafka and cache them by timestamp."""
    for message in anomaly_consumer:
        anomaly_data = message.value
        timestamp = anomaly_data['timestamp']
        maintenance_flag = anomaly_data.get('maintenance_flag', 0)
        anomaly_cache[timestamp] = maintenance_flag

def write_to_influxdb(batch_df):
    """Write cleaned data along with anomalies to InfluxDB."""
    try:
        data = []
        for row in batch_df.collect():
            if row["timestamp"] is None:
                print("Timestamp is None, skipping this row.")
                continue

            timestamp = row["timestamp"]
            maintenance_flag = anomaly_cache.pop(timestamp, 0)  # Fetch and remove from cache
            timestamp_ns = int(timestamp.timestamp()) * 1000000000  # Convert to nanoseconds

            data.append({
                "measurement": "cleaned_sensor_data",
                "tags": {
                    "source": "spark",
                    "train_id": row["train_id"]
                },
                "fields": {key: row[key] for key in row.asDict() if key not in ['timestamp', 'train_id']},
                "time": timestamp_ns
            })

        if data:
            influx_client.write_points(data)
            print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write to InfluxDB: {e}")

# Define schema for sensor data
schema = StructType() \
    .add("timestamp", TimestampType()) \
    .add("train_id", StringType()) \
    .add("TP2", FloatType()) \
    .add("TP3", FloatType()) \
    .add("H1", FloatType()) \
    .add("DV_pressure", FloatType()) \
    .add("Reservoirs", FloatType()) \
    .add("Oil_temperature", FloatType()) \
    .add("Motor_current", FloatType()) \
    .add("COMP", IntegerType()) \
    .add("DV_eletric", IntegerType()) \
    .add("Towers", IntegerType()) \
    .add("MPG", IntegerType()) \
    .add("LPS", IntegerType()) \
    .add("Pressure_switch", IntegerType()) \
    .add("Oil_level", IntegerType()) \
    .add("Caudal_impulses", IntegerType())

def main():
    # Start Spark session
    spark = SparkSession.builder \
        .appName("Sensor Data Cleaning") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Start thread to fetch anomalies
    anomaly_thread = Thread(target=fetch_anomalies, daemon=True)
    anomaly_thread.start()

    # Read data from Kafka topics for each train
    raw_data = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "fulldata_train1,fulldata_train2") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    # Parse JSON data
    parsed_data = raw_data.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Ensure the timestamp is valid
    parsed_data = parsed_data.withColumn(
        "timestamp", when(col("timestamp").isNull(), current_timestamp()).otherwise(col("timestamp"))
    )

    # Min and max ranges for each feature
    min_values = {
        "TP2": -0.032, "TP3": 0.73, "H1": -0.036, "DV_pressure": -0.032,
        "Reservoirs": 0.712, "Oil_temperature": 15.4, "Motor_current": 0.02,
        "COMP": 0, "DV_eletric": 0, "Towers": 0, "MPG": 0, "LPS": 0,
        "Pressure_switch": 0, "Oil_level": 0, "Caudal_impulses": 0
    }
    max_values = {
        "TP2": 10.676, "TP3": 10.302, "H1": 10.288, "DV_pressure": 9.844,
        "Reservoirs": 10.3, "Oil_temperature": 89.05, "Motor_current": 9.295,
        "COMP": 1, "DV_eletric": 1, "Towers": 1, "MPG": 1, "LPS": 1,
        "Pressure_switch": 1, "Oil_level": 1, "Caudal_impulses": 1
    }

    # Build filter conditions dynamically and combine them using reduce
    conditions = reduce(
        lambda a, b: a & b,
        [col(feature).between(min_values[feature], max_values[feature]) for feature in min_values.keys()]
    )

    # Apply the combined condition to filter the data
    cleaned_data = parsed_data.filter(conditions)

    # Write cleaned data to InfluxDB
    cleaned_data.writeStream \
        .foreachBatch(lambda batch_df, batch_id: write_to_influxdb(batch_df)) \
        .start()

    # Write cleaned data back to Kafka
    cleaned_data.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "cleaned_sensor_data") \
        .option("checkpointLocation", "/tmp/spark_clean_checkpoint") \
        .start() \
        .awaitTermination()

if __name__ == "__main__":
    main()
