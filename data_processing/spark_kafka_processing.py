from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, FloatType, TimestampType

# Define the schema for combined sensor data
schema = StructType() \
    .add("timestamp", TimestampType()) \
    .add("temperature", FloatType()) \
    .add("vibration", FloatType())

def main():
    # Create SparkSession
    spark = SparkSession.builder \
        .appName("Combined Sensor Data Processing") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Read data from Kafka (Raw data from sensrs ...)
    raw_data = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "combined_sensor_data") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse the JSON data
    parsed_data = raw_data.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Filter invalid data cleaning , agreeragtion ::: mission value etc
    cleaned_data = parsed_data.filter(
        (col("temperature").between(10.0, 50.0)) &  # Valid temperature range
        (col("vibration").between(0.0, 10.0))       # Valid vibration range
    )

    # Write cleaned data to a new Kafka topic
    query = cleaned_data.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "cleaned_combined_data") \
        .option("checkpointLocation", "/tmp/spark_checkpoint_combined") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
