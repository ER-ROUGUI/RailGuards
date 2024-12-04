import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class VibrationPublisher(Node):
    def __init__(self):
        super().__init__('vibration_publisher')
        self.publisher_ = self.create_publisher(Float32, 'vibration_data', 10)
        self.timer = self.create_timer(1.0, self.publish_data)  # Publish every 1 second

    def publish_data(self):
        vibration_value = random.uniform(0.0, 10.0)  # Simulate vibration data (e.g., G-force)
        self.publisher_.publish(Float32(data=vibration_value))
        self.get_logger().info(f'Published vibration data: {vibration_value}')

def main(args=None):
    rclpy.init(args=args)
    node = VibrationPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
