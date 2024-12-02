from kafka import KafkaProducer, KafkaConsumer
import time

# Kafka configuration
BROKER_IP = "localhost"  # Replace with the IP of the Kafka broker
INPUT_TOPIC = "cleaned_sensor_data"  # Input topic to subscribe to
OUTPUT_TOPIC = "remote_topic"         # Output topic to send messages to

# Initialize Kafka producer and consumer
producer = KafkaProducer(bootstrap_servers=f"{BROKER_IP}:9092")
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=f"{BROKER_IP}:9092",
    group_id="forwarding_group",  # Unique group ID for the consumer
    auto_offset_reset="earliest"  # Start from the beginning if no offset is committed
)

def forward_data():
    print("Starting to forward data from cleaned_combined_data to remote_topic...")
    try:
        for message in consumer:  # Listen for new messages
            processed_message = f"Processed: {message.value.decode('utf-8')}"
            producer.send(OUTPUT_TOPIC, processed_message.encode('utf-8'))
            print(f"Forwarded: {processed_message}")
    except KeyboardInterrupt:
        print("Stopped forwarding data.")
    finally:
        consumer.close()
        producer.close()

if __name__ == "__main__":
    forward_data()
