import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool , Int32
from kafka import KafkaProducer
import json
import time


class FullSensorROS2KafkaBridge(Node):
    def __init__(self):
        super().__init__('full_ros2_kafka_bridge')

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

        # Initialize variables for all sensors
        self.sensors = {
            "TP2": None,
            "TP3": None,
            "H1": None,
            "DV_pressure": None,
            "Reservoirs": None,
            "Oil_temperature": None,
            "Motor_current": None,
            "COMP": None,
            "DV_eletric": None,
            "Towers": None,
            "MPG": None,
            "LPS": None,
            "Pressure_switch": None,
            "Oil_level": None,
            "Caudal_impulses": None
        }

        # Topic-to-sensor mapping for analog sensors
        self.analog_topics = {
            'TP2': 'TP2',
            'TP3': 'TP3',
            'H1': 'H1',
            'DV_pressure': 'DV_pressure',
            'Reservoirs': 'Reservoirs',
            'Oil_temperature': 'Oil_temperature',
            'Motor_current': 'Motor_current'
        }

        # Topic-to-sensor mapping for digital sensors
        self.digital_topics = {
            'COMP': 'COMP',
            'DV_eletric': 'DV_eletric',
            'Towers': 'Towers',
            'MPG': 'MPG',
            'LPS': 'LPS',
            'Pressure_switch': 'Pressure_switch',
            'Oil_level': 'Oil_level',
            'Caudal_impulses': 'Caudal_impulses'
        }

        # Subscriptions for analog sensors
        for topic, sensor in self.analog_topics.items():
            self.create_subscription(Float32, topic, lambda msg, s=sensor: self.analog_callback(msg, s), 10)

        # Subscriptions for digital sensors
        for topic, sensor in self.digital_topics.items():
            self.create_subscription(Int32, topic, lambda msg, s=sensor: self.digital_callback(msg, s), 10)

        # Timer to send combined data to Kafka
        self.timer = self.create_timer(1.0, self.send_combined_data)

    def analog_callback(self, msg, sensor_name):
        self.sensors[sensor_name] = msg.data
        self.get_logger().info(f"Updated {sensor_name}: {msg.data}")

    def digital_callback(self, msg, sensor_name):
        self.sensors[sensor_name] = msg.data
        self.get_logger().info(f"Updated {sensor_name}: {msg.data}")

    def send_combined_data(self):
        # Combine all sensor data and send to Kafka
        combined_data = {
            "timestamp": time.time(),
            **self.sensors
        }

        # Check for None values to ensure completeness
        missing_sensors = [key for key, value in self.sensors.items() if value is None]
        if missing_sensors:
            self.get_logger().warning(f"Missing sensor data for: {missing_sensors}")

        try:
            self.kafka_producer.send('fulldata', combined_data)
            self.get_logger().info(f"Sent combined data to Kafka: {combined_data}")
        except Exception as e:
            self.get_logger().error(f"Failed to send data to Kafka: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = FullSensorROS2KafkaBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down node...")
    finally:
        node.destroy_node()
        if rclpy.ok():  # Ensure shutdown is only called if rclpy is still active
            rclpy.shutdown()


if __name__ == '__main__':
    main()
