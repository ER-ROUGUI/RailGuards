import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32
from kafka import KafkaProducer
import json
import time


class MultiTrainROS2KafkaBridge(Node):
    def __init__(self):
        super().__init__('multi_train_ros2_kafka_bridge')

        # Initialize Kafka producer
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers='localhost:9092',  # Replace with your Kafka broker address
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.get_logger().info("Connected to Kafka broker successfully.")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to Kafka broker: {e}")
            raise e

        # List of train IDs
        self.train_ids = ['train1', 'train2']

        # Initialize data storage for all trains
        self.trains_data = {
            train_id: {sensor: None for sensor in self.get_sensor_list()} for train_id in self.train_ids
        }

        # Subscribe to all topics dynamically
        for train_id in self.train_ids:
            for sensor in self.get_sensor_list():
                topic_name = f'/{train_id}/{sensor}'
                msg_type = Float32 if sensor in self.get_analog_sensors() else Int32
                self.create_subscription(msg_type, topic_name, lambda msg, t=train_id, s=sensor: self.sensor_callback(msg, t, s), 10)

        # Timer to send combined data to Kafka
        self.timer = self.create_timer(1.0, self.send_combined_data)

    def get_sensor_list(self):
        """Get a list of all sensors."""
        return [
            'TP2', 'TP3', 'H1', 'DV_pressure', 'Reservoirs', 'Oil_temperature', 'Motor_current',
            'COMP', 'DV_eletric', 'Towers', 'MPG', 'LPS', 'Pressure_switch', 'Oil_level', 'Caudal_impulses'
        ]

    def get_analog_sensors(self):
        """Get a list of analog sensors."""
        return ['TP2', 'TP3', 'H1', 'DV_pressure', 'Reservoirs', 'Oil_temperature', 'Motor_current']

    def sensor_callback(self, msg, train_id, sensor_name):
        """Update the sensor data for the specified train."""
        self.trains_data[train_id][sensor_name] = msg.data
        self.get_logger().info(f"[{train_id}] Updated {sensor_name}: {msg.data}")

    def send_combined_data(self):
        """Send combined data for each train to Kafka."""
        for train_id, data in self.trains_data.items():
            combined_data = {
                "timestamp": time.time(),
                "train_id": train_id,
                **data
            }

            # Check for None values and log warnings
            missing_sensors = [key for key, value in data.items() if value is None]
            if missing_sensors:
                self.get_logger().warning(f"[{train_id}] Missing sensor data for: {missing_sensors}")

            # Determine the Kafka topic for the train
            kafka_topic = f'fulldata_{train_id}'

            # Send to Kafka
            try:
                self.kafka_producer.send(kafka_topic, combined_data)  # Unified topic
                self.get_logger().info(f"Sent combined data to {kafka_topic} for {train_id}: {combined_data}")
            except Exception as e:
                self.get_logger().error(f"Failed to send data to {kafka_topic} for {train_id}: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = MultiTrainROS2KafkaBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
