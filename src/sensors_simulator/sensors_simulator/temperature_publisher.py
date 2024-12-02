import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import random

class MockSensorPublisher(Node):
    def __init__(self):
        super().__init__('temperature_publisher')
        self.publisher_ = self.create_publisher(Float32, 'temperature_data', 10)
        self.timer = self.create_timer(1.0, self.publish_data)

    def publish_data(self):

        # Generate correct temperature 90% of the time
        if random.random() < 0.9:
            temperature = random.uniform(20.0, 30.0)  # Correct range
        else:
            # Generate incorrect temperature 10% of the time
            temperature = random.uniform(-50.0, 100.0)  # Incorrect range

        self.publisher_.publish(Float32(data=temperature))
        self.get_logger().info(f'Published temperature: {temperature}')

def main(args=None):
    rclpy.init(args=args)
    node = MockSensorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
