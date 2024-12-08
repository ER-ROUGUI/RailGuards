import random
import time
from std_msgs.msg import Float32, Bool , Int32, String
import rclpy
from rclpy.node import Node

class FullSensorPublisher(Node):
    def __init__(self):
        super().__init__('full_sensor_publisher')

        # Train ID for this publisher


        # Analog sensor publishers (7) renamed to match dataset features
        self.tp2_pub = self.create_publisher(Float32, 'TP2', 10)
        self.tp3_pub = self.create_publisher(Float32, 'TP3', 10)
        self.h1_pub = self.create_publisher(Float32, 'H1', 10)
        self.dv_pressure_pub = self.create_publisher(Float32, 'DV_pressure', 10)
        self.reservoirs_pub = self.create_publisher(Float32, 'Reservoirs', 10)
        self.oil_temperature_pub = self.create_publisher(Float32, 'Oil_temperature', 10)
        self.motor_current_pub = self.create_publisher(Float32, 'Motor_current', 10)

        # Digital sensor publishers (8) renamed to match dataset features
        self.comp_pub = self.create_publisher(Int32, 'COMP', 10)
        self.dv_eletric_pub = self.create_publisher(Int32, 'DV_eletric', 10)
        self.towers_pub = self.create_publisher(Int32, 'Towers', 10)
        self.mpg_pub = self.create_publisher(Int32, 'MPG', 10)
        self.lps_pub = self.create_publisher(Int32, 'LPS', 10)
        self.pressure_switch_pub = self.create_publisher(Int32, 'Pressure_switch', 10)
        self.oil_level_pub = self.create_publisher(Int32, 'Oil_level', 10)
        self.caudal_impulses_pub = self.create_publisher(Int32, 'Caudal_impulses', 10)

        # Timer for publishing data
        self.timer = self.create_timer(1.0, self.publish_data)  # Publish at 1 Hz

    def inject_fault(self, value, min_val, max_val, fault_probability=0.1):
        """
        Inject a fault with the given probability by generating out-of-range values.
        """
        if random.random() < fault_probability:  # Introduce fault with the specified probability
            # Generate an out-of-range value
            if random.choice([True, False]):  # Randomly decide whether it's below or above the range
                return random.uniform(min_val - 10, min_val - 1)  # Below range
            else:
                return random.uniform(max_val + 1, max_val + 10)  # Above range
        return value

    def publish_data(self):

        # Min and max ranges for each sensor
        ranges = {
            "TP2": (-0.032, 10.676),
            "TP3": (0.73, 10.302),
            "H1": (-0.036, 10.288),
            "DV_pressure": (-0.032, 9.844),
            "Reservoirs": (0.712, 10.3),
            "Oil_temperature": (15.4, 89.05),
            "Motor_current": (0.02, 9.295)
        }

        def generate_value(min_val, max_val, fault_probability=0.1):
            """Generate a value within range, occasionally injecting faults."""
            if random.random() < fault_probability:  # Inject fault
                # Generate an out-of-range value
                if random.choice([True, False]):  # Below or above the range
                    return random.uniform(min_val - 10, min_val - 1)
                else:
                    return random.uniform(max_val + 1, max_val + 10)
            return random.uniform(min_val, max_val)  # Within range

        # Generate values for each sensor
        tp2 = generate_value(*ranges["TP2"])
        tp3 = generate_value(*ranges["TP3"])
        h1 = generate_value(*ranges["H1"])
        dv_pressure = generate_value(*ranges["DV_pressure"])
        reservoirs = generate_value(*ranges["Reservoirs"])
        oil_temperature = generate_value(*ranges["Oil_temperature"])
        motor_current = generate_value(*ranges["Motor_current"])

        self.tp2_pub.publish(Float32(data=tp2))
        self.tp3_pub.publish(Float32(data=tp3))
        self.h1_pub.publish(Float32(data=h1))
        self.dv_pressure_pub.publish(Float32(data=dv_pressure))
        self.reservoirs_pub.publish(Float32(data=reservoirs))
        self.oil_temperature_pub.publish(Float32(data=oil_temperature))
        self.motor_current_pub.publish(Float32(data=motor_current))

        # Generate and publish digital sensor data (0 for False, 1 for True)
        self.comp_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.dv_eletric_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.towers_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.mpg_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.lps_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.pressure_switch_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.oil_level_pub.publish(Int32(data=int(random.choice([0, 1]))))
        self.caudal_impulses_pub.publish(Int32(data=int(random.choice([0, 1]))))

        # Log published data with fault status
        fault_injected = any([
            not (ranges["TP2"][0] <= tp2 <= ranges["TP2"][1]),
            not (ranges["TP3"][0] <= tp3 <= ranges["TP3"][1]),
            not (ranges["H1"][0] <= h1 <= ranges["H1"][1]),
            not (ranges["DV_pressure"][0] <= dv_pressure <= ranges["DV_pressure"][1]),
            not (ranges["Reservoirs"][0] <= reservoirs <= ranges["Reservoirs"][1]),
            not (ranges["Oil_temperature"][0] <= oil_temperature <= ranges["Oil_temperature"][1]),
            not (ranges["Motor_current"][0] <= motor_current <= ranges["Motor_current"][1]),
        ])
        self.get_logger().info(f"Published sensor data. Fault injected: {fault_injected}")

def main(args=None):
    rclpy.init(args=args)
    node = FullSensorPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()