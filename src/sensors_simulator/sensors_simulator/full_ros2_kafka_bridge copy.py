import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from kafka import KafkaProducer
import json
import time


class FullSensorROS2KafkaBridge(Node):
    def __init__(self):
        super().__init__('full_ros2_kafka_bridge')

        # Initialize Kafka producer
        self.kafka_producer = KafkaProducer(
            bootstrap_servers='localhost:9092',  # Replace with your Kafka broker address
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Initialize variables for all sensors
        self.sensors = {
            "pressure": None,
            "oil_temperature": None,
            "motor_current": None,
            "air_temperature": None,
            "humidity": None,
            "vibration": None,
            "air_pressure": None,
            "valve_intake": None,
            "valve_outlet": None,
            "compressor_status": None,
            "filter_status": None,
            "safety_switch": None,
            "overload_protection": None,
            "emergency_stop": None,
            "door_sensor": None
        }

        # Topic-to-sensor mapping for analog sensors
        self.analog_topics = {
            'pressure': 'pressure',
            'oil_temperature': 'oil_temperature',
            'motor_current': 'motor_current',
            'air_temperature': 'air_temperature',
            'humidity': 'humidity',
            'vibration': 'vibration',
            'air_pressure': 'air_pressure'
        }

        # Topic-to-sensor mapping for digital sensors
        self.digital_topics = {
            'valve_intake': 'valve_intake',
            'valve_outlet': 'valve_outlet',
            'compressor_status': 'compressor_status',
            'filter_status': 'filter_status',
            'safety_switch': 'safety_switch',
            'overload_protection': 'overload_protection',
            'emergency_stop': 'emergency_stop',
            'door_sensor': 'door_sensor'
        }

        # Subscriptions for analog sensors
        for topic, sensor in self.analog_topics.items():
            self.create_subscription(Float32, topic, lambda msg, s=sensor: self.analog_callback(msg, s), 10)

        # Subscriptions for digital sensors
        for topic, sensor in self.digital_topics.items():
            self.create_subscription(Bool, topic, lambda msg, s=sensor: self.digital_callback(msg, s), 10)

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
        self.kafka_producer.send('fulldata', combined_data)
        self.get_logger().info(f"Sent combined data to Kafka: {combined_data}")


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
