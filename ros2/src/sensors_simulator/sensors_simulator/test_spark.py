from pyspark.sql import SparkSession

def main():
    # Create SparkSession
    spark = SparkSession.builder \
        .appName("Test Kafka Stream") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Read data from Kafka
    raw_data = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "sensor_data") \
        .option("startingOffsets", "earliest") \
        .load()

    # Write the raw Kafka data to the console
    query = raw_data.writeStream \
        .format("console") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
