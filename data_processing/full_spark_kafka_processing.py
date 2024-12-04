from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, current_timestamp, lit
from pyspark.sql.types import StructType, FloatType, BooleanType, TimestampType , IntegerType
from influxdb import InfluxDBClient
from datetime import datetime
from functools import reduce
from pyspark.sql.functions import col
from kafka import KafkaConsumer
import json


# InfluxDB 1.x configuration
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


def fetch_anomalies():
    """Fetch anomalies from Kafka and cache them by timestamp."""
    for message in anomaly_consumer:
        anomaly_data = message.value
        timestamp = anomaly_data['timestamp']
        maintenance_flag = anomaly_data.get('maintenance_flag', 0)
        anomaly_cache[timestamp] = maintenance_flag


# def write_to_influxdb(batch_df):
#     """
#     Write cleaned data from Spark batch to InfluxDB 1.x.
#     """
#     try:
#         data = []
#         for row in batch_df.collect():
#             if row["timestamp"] is None:
#                 print("Timestamp is None, skipping this row.")
#                 continue
            
#             timestamp = int(row["timestamp"].timestamp()) * 1000000000
#             data.append({
#                 "measurement": "cleaned_sensor_data",
#                 "tags": {"source": "spark"},
#                 "fields": {
#                     "TP2": row["TP2"],
#                     "TP3": row["TP3"],
#                     "H1": row["H1"],
#                     "DV_pressure": row["DV_pressure"],
#                     "Reservoirs": row["Reservoirs"],
#                     "Oil_temperature": row["Oil_temperature"],
#                     "Motor_current": row["Motor_current"],
#                     "COMP": row["COMP"],
#                     "DV_eletric": row["DV_eletric"],
#                     "Towers": row["Towers"],
#                     "MPG": row["MPG"],
#                     "LPS": row["LPS"],
#                     "Pressure_switch": row["Pressure_switch"],
#                     "Oil_level": row["Oil_level"],
#                     "Caudal_impulses": row["Caudal_impulses"]
#                 },
#                 "time": timestamp
#             })

#         if data:
#             influx_client.write_points(data)
#             print(f"Data written to InfluxDB: {data}")
#     except Exception as e:
#         print(f"Failed to write to InfluxDB: {e}")


def write_to_influxdb(batch_df):
    """
    Write cleaned data along with anomalies to InfluxDB.
    """
    try:
        data = []
        for row in batch_df.collect():
            if row["timestamp"] is None:
                print("Timestamp is None, skipping this row.")
                continue

            timestamp = row["timestamp"]
            maintenance_flag = anomaly_cache.pop(timestamp, 0)  # Fetch and remove from cache

            # Convert timestamp to nanoseconds
            timestamp_ns = int(timestamp.timestamp()) * 1000000000

            data.append({
                "measurement": "cleaned_sensor_data",
                "tags": {"source": "spark"},
                "fields": {
                    "TP2": row["TP2"],
                    "TP3": row["TP3"],
                    "H1": row["H1"],
                    "DV_pressure": row["DV_pressure"],
                    "Reservoirs": row["Reservoirs"],
                    "Oil_temperature": row["Oil_temperature"],
                    "Motor_current": row["Motor_current"],
                    "COMP": row["COMP"],
                    "DV_eletric": row["DV_eletric"],
                    "Towers": row["Towers"],
                    "MPG": row["MPG"],
                    "LPS": row["LPS"],
                    "Pressure_switch": row["Pressure_switch"],
                    "Oil_level": row["Oil_level"],
                    "Caudal_impulses": row["Caudal_impulses"],
                    "maintenance_flag": maintenance_flag
                },
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
    .add("TP2", FloatType()) \
    .add("TP3", FloatType()) \
    .add("H1", FloatType()) \
    .add("DV_pressure", FloatType()) \
    .add("Reservoirs", FloatType()) \
    .add("Oil_temperature", FloatType()) \
    .add("Motor_current", FloatType()) \
    .add("COMP", FloatType()) \
    .add("DV_eletric", FloatType()) \
    .add("Towers", FloatType()) \
    .add("MPG", FloatType()) \
    .add("LPS", FloatType()) \
    .add("Pressure_switch", FloatType()) \
    .add("Oil_level", FloatType()) \
    .add("Caudal_impulses", FloatType())

def main():


    spark = SparkSession.builder \
        .appName("Sensor Data Cleaning") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Read data from Kafka
    raw_data = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "fulldata") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON data
    parsed_data = raw_data.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")


    # Start thread to fetch anomalies
    from threading import Thread
    anomaly_thread = Thread(target=fetch_anomalies, daemon=True)
    anomaly_thread.start()


    # Ensure the timestamp is valid
    parsed_data = parsed_data.withColumn(
        "timestamp", when(col("timestamp").isNull(), current_timestamp()).otherwise(col("timestamp"))
    )

    # Cast digital variables to integers
    digital_columns = [
        "COMP", "DV_eletric", "Towers", "MPG", "LPS",
        "Pressure_switch", "Oil_level", "Caudal_impulses"
    ]

    for col_name in digital_columns:
        parsed_data = parsed_data.withColumn(col_name, col(col_name).cast(IntegerType()))

    # Add maintenance_flag column initialized to 0
    parsed_data = parsed_data.withColumn("maintenance_flag", lit(0).cast(IntegerType()))

    min_values = {
    "TP2": -0.032,
    "TP3": 0.73,
    "H1": -0.036,
    "DV_pressure": -0.032,
    "Reservoirs": 0.712,
    "Oil_temperature": 15.4,
    "Motor_current": 0.02,
    "COMP": 0.0,
    "DV_eletric": 0.0,
    "Towers": 0.0,
    "MPG": 0.0,
    "LPS": 0.0,
    "Pressure_switch": 0.0,
    "Oil_level": 0.0,
    "Caudal_impulses": 0.0
    }

    max_values = {
        "TP2": 10.676,
        "TP3": 10.302,
        "H1": 10.288,
        "DV_pressure": 9.844,
        "Reservoirs": 10.3,
        "Oil_temperature": 89.05,
        "Motor_current": 9.295,
        "COMP": 1.0,
        "DV_eletric": 1.0,
        "Towers": 1.0,
        "MPG": 1.0,
        "LPS": 1.0,
        "Pressure_switch": 1.0,
        "Oil_level": 1.0,
        "Caudal_impulses": 1.0
    }

    # Build filter conditions dynamically and combine them using reduce
    conditions = reduce(
        lambda a, b: a & b,
        [col(feature).between(min_values[feature], max_values[feature]) for feature in min_values.keys()]
    )

    # Apply the combined condition to filter the data
    cleaned_data = parsed_data.filter(conditions)

    # # Filter invalid data
    # cleaned_data = parsed_data.filter(
    #     (col("TP2").between(-10.0, 10.0)) &
    #     (col("TP3").between(0.0, 20.0)) &
    #     (col("H1").between(-5.0, 15.0)) &
    #     (col("DV_pressure").between(0.0, 5.0)) &
    #     (col("Reservoirs").between(10.0, 50.0)) &
    #     (col("Oil_temperature").between(20.0, 100.0)) &
    #     (col("Motor_current").between(0.1, 5.0)) &
    #     (col("COMP").between(0, 1)) &
    #     (col("DV_eletric").between(0, 1)) &
    #     (col("Towers").between(0, 1)) &
    #     (col("MPG").between(0, 1)) &
    #     (col("LPS").between(0, 1)) &
    #     (col("Pressure_switch").between(0, 1)) &
    #     (col("Oil_level").between(0, 1)) &
    #     (col("Caudal_impulses").between(0, 1))
    # )


    # Write to InfluxDB
    cleaned_data.writeStream \
        .foreachBatch(lambda batch_df, batch_id: write_to_influxdb(batch_df)) \
        .start()

    # Write cleaned data to Kafka
    query = cleaned_data.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "cleaned_sensor_data") \
        .option("checkpointLocation", "/tmp/spark_clean_checkpoint") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
