import random
import time
from std_msgs.msg import Float32, Bool
import rclpy
from rclpy.node import Node

class FullSensorPublisher(Node):
    def __init__(self):
        super().__init__('full_sensor_publisher')

        # Analog sensor publishers (7)
        self.pressure_pub = self.create_publisher(Float32, 'pressure', 10)
        self.oil_temp_pub = self.create_publisher(Float32, 'oil_temperature', 10)
        self.motor_current_pub = self.create_publisher(Float32, 'motor_current', 10)
        self.air_temp_pub = self.create_publisher(Float32, 'air_temperature', 10)
        self.humidity_pub = self.create_publisher(Float32, 'humidity', 10)
        self.vibration_pub = self.create_publisher(Float32, 'vibration', 10)
        self.air_pressure_pub = self.create_publisher(Float32, 'air_pressure', 10)

        # Digital sensor publishers (8)
        self.valve_intake_pub = self.create_publisher(Bool, 'valve_intake', 10)
        self.valve_outlet_pub = self.create_publisher(Bool, 'valve_outlet', 10)
        self.compressor_status_pub = self.create_publisher(Bool, 'compressor_status', 10)
        self.filter_status_pub = self.create_publisher(Bool, 'filter_status', 10)
        self.safety_switch_pub = self.create_publisher(Bool, 'safety_switch', 10)
        self.overload_protection_pub = self.create_publisher(Bool, 'overload_protection', 10)
        self.emergency_stop_pub = self.create_publisher(Bool, 'emergency_stop', 10)
        self.door_sensor_pub = self.create_publisher(Bool, 'door_sensor', 10)

        # Timer for publishing data
        self.timer = self.create_timer(1.0, self.publish_data)  # Publish at 1 Hz

    def inject_fault(self, value, min_val, max_val, fault_probability=0.2):
        """Inject a fault with the given probability."""
        if random.random() < fault_probability:  # Lower probability for faults
            return random.uniform(min_val - 10, min_val - 1)  # Faulty value
        return value

    def publish_data(self):
        # Generate and publish analog sensor data with fault injection
        pressure = self.inject_fault(random.uniform(1.0, 10.0), 1.0, 10.0)
        oil_temp = self.inject_fault(random.uniform(30.0, 90.0), 30.0, 90.0)
        motor_current = self.inject_fault(random.uniform(0.5, 5.0), 0.5, 5.0)
        air_temp = self.inject_fault(random.uniform(15.0, 40.0), 15.0, 40.0)
        humidity = self.inject_fault(random.uniform(30.0, 90.0), 30.0, 90.0)
        vibration = self.inject_fault(random.uniform(0.1, 2.0), 0.1, 2.0)
        air_pressure = self.inject_fault(random.uniform(1.0, 10.0), 1.0, 10.0)

        self.pressure_pub.publish(Float32(data=pressure))
        self.oil_temp_pub.publish(Float32(data=oil_temp))
        self.motor_current_pub.publish(Float32(data=motor_current))
        self.air_temp_pub.publish(Float32(data=air_temp))
        self.humidity_pub.publish(Float32(data=humidity))
        self.vibration_pub.publish(Float32(data=vibration))
        self.air_pressure_pub.publish(Float32(data=air_pressure))

        # Generate and publish digital sensor data
        self.valve_intake_pub.publish(Bool(data=random.choice([True, False])))
        self.valve_outlet_pub.publish(Bool(data=random.choice([True, False])))
        self.compressor_status_pub.publish(Bool(data=random.choice([True, False])))
        self.filter_status_pub.publish(Bool(data=random.choice([True, False])))
        self.safety_switch_pub.publish(Bool(data=random.choice([True, False])))
        self.overload_protection_pub.publish(Bool(data=random.choice([True, False])))
        self.emergency_stop_pub.publish(Bool(data=random.choice([True, False])))
        self.door_sensor_pub.publish(Bool(data=random.choice([True, False])))

        # Log published data with fault status
        fault_injected = any([
            pressure < 1.0 or pressure > 10.0,
            oil_temp < 30.0 or oil_temp > 90.0,
            motor_current < 0.5 or motor_current > 5.0,
            air_temp < 15.0 or air_temp > 40.0,
            humidity < 30.0 or humidity > 90.0,
            vibration < 0.1 or vibration > 2.0,
            air_pressure < 1.0 or air_pressure > 10.0,
        ])
        self.get_logger().info(f"Published sensor data. Fault injected: {fault_injected}")

def main(args=None):
    rclpy.init(args=args)
    node = FullSensorPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
