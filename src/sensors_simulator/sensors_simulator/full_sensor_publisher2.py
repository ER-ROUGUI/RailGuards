import random
import time
from std_msgs.msg import Float32, Int32
import rclpy
from rclpy.node import Node

class DualTrainSensorPublisher(Node):
    def __init__(self):
        super().__init__('dual_train_sensor_publisher')

        # Train IDs
        self.train_ids = ["train_1", "train_2"]
        self.current_train_index = 0  # Index to alternate between train IDs

        # Analog sensor publishers (shared across train IDs)
        self.analog_publishers = {
            'TP2': self.create_publisher(Float32, 'TP2', 10),
            'TP3': self.create_publisher(Float32, 'TP3', 10),
            'H1': self.create_publisher(Float32, 'H1', 10),
            'DV_pressure': self.create_publisher(Float32, 'DV_pressure', 10),
            'Reservoirs': self.create_publisher(Float32, 'Reservoirs', 10),
            'Oil_temperature': self.create_publisher(Float32, 'Oil_temperature', 10),
            'Motor_current': self.create_publisher(Float32, 'Motor_current', 10)
        }

        # Digital sensor publishers (shared across train IDs)
        self.digital_publishers = {
            'COMP': self.create_publisher(Int32, 'COMP', 10),
            'DV_eletric': self.create_publisher(Int32, 'DV_eletric', 10),
            'Towers': self.create_publisher(Int32, 'Towers', 10),
            'MPG': self.create_publisher(Int32, 'MPG', 10),
            'LPS': self.create_publisher(Int32, 'LPS', 10),
            'Pressure_switch': self.create_publisher(Int32, 'Pressure_switch', 10),
            'Oil_level': self.create_publisher(Int32, 'Oil_level', 10),
            'Caudal_impulses': self.create_publisher(Int32, 'Caudal_impulses', 10)
        }

        # Timer for publishing data
        self.timer = self.create_timer(1.0, self.publish_data)  # Publish at 1 Hz

    def generate_value(self, min_val, max_val, fault_probability=0.1):
        """Generate a sensor value within range, occasionally injecting faults."""
        if random.random() < fault_probability:  # Inject fault
            # Generate an out-of-range value
            if random.choice([True, False]):  # Below or above the range
                return random.uniform(min_val - 10, min_val - 1)
            else:
                return random.uniform(max_val + 1, max_val + 10)
        return random.uniform(min_val, max_val)  # Within range

    def publish_data(self):
        # Current train ID
        train_id = self.train_ids[self.current_train_index]

        # Toggle train for the next iteration
        self.current_train_index = (self.current_train_index + 1) % len(self.train_ids)

        # Define sensor ranges
        ranges = {
            "TP2": (-0.032, 10.676),
            "TP3": (0.73, 10.302),
            "H1": (-0.036, 10.288),
            "DV_pressure": (-0.032, 9.844),
            "Reservoirs": (0.712, 10.3),
            "Oil_temperature": (15.4, 89.05),
            "Motor_current": (0.02, 9.295)
        }

        # Publish analog sensor data
        for sensor_name, publisher in self.analog_publishers.items():
            value = self.generate_value(*ranges[sensor_name])
            publisher.publish(Float32(data=value))
            self.get_logger().info(f"[{train_id}] Published {sensor_name}: {value}")

        # Publish digital sensor data (0 or 1)
        for sensor_name, publisher in self.digital_publishers.items():
            value = random.choice([0, 1])
            publisher.publish(Int32(data=value))
            self.get_logger().info(f"[{train_id}] Published {sensor_name}: {value}")

        # Log train ID
        self.get_logger().info(f"Data published for {train_id}")

def main(args=None):
    rclpy.init(args=args)
    node = DualTrainSensorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down node...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
