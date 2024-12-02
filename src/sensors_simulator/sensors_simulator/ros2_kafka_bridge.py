import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from kafka import KafkaProducer
import json
import time

class CombinedROS2KafkaBridge(Node):
    def __init__(self):
        super().__init__('ros2_kafka_bridge')
        self.kafka_producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        self.temperature = None
        self.vibration = None
        ## Add more sensors here like those that mesure ....

        self.create_subscription(Float32, 'temperature_data', self.sensor_callback, 10)
        self.create_subscription(Float32, 'vibration_data', self.vibration_callback, 10)
        self.timer = self.create_timer(1.0, self.send_combined_data)

    def sensor_callback(self, msg):
        self.temperature = msg.data
        self.get_logger().info(f"Updated temperature: {msg.data}")

    def vibration_callback(self, msg):
        self.vibration = msg.data
        self.get_logger().info(f"Updated vibration: {msg.data}")

    def send_combined_data(self):
        if self.temperature is not None and self.vibration is not None:
            combined_data = {
                "timestamp": time.time(),
                "temperature": self.temperature,
                "vibration": self.vibration
            }
            self.kafka_producer.send('combined_sensor_data', combined_data)
            self.get_logger().info(f"Sent combined data to Kafka: {combined_data}")

def main(args=None):
    rclpy.init(args=args)
    node = CombinedROS2KafkaBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
