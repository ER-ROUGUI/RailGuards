import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32

class Train1SensorPublisher(Node):
    def __init__(self):
        super().__init__('train1_sensor_publisher')

        train1 = "train1"

        # Analog sensor publishers
        self.tp2_pub = self.create_publisher(Float32, f'{train1}/TP2', 10)
        self.tp3_pub = self.create_publisher(Float32, f'{train1}/TP3', 10)
        self.h1_pub = self.create_publisher(Float32, f'{train1}/H1', 10)
        self.dv_pressure_pub = self.create_publisher(Float32, f'{train1}/DV_pressure', 10)
        self.reservoirs_pub = self.create_publisher(Float32, f'{train1}/Reservoirs', 10)
        self.oil_temperature_pub = self.create_publisher(Float32, f'{train1}/Oil_temperature', 10)
        self.motor_current_pub = self.create_publisher(Float32, f'{train1}/Motor_current', 10)

        # Digital sensor publishers
        self.comp_pub = self.create_publisher(Int32, f'{train1}/COMP', 10)
        self.dv_eletric_pub = self.create_publisher(Int32, f'{train1}/DV_eletric', 10)
        self.towers_pub = self.create_publisher(Int32, f'{train1}/Towers', 10)
        self.mpg_pub = self.create_publisher(Int32, f'{train1}/MPG', 10)
        self.lps_pub = self.create_publisher(Int32, f'{train1}/LPS', 10)
        self.pressure_switch_pub = self.create_publisher(Int32, f'{train1}/Pressure_switch', 10)
        self.oil_level_pub = self.create_publisher(Int32, f'{train1}/Oil_level', 10)
        self.caudal_impulses_pub = self.create_publisher(Int32, f'{train1}/Caudal_impulses', 10)

        # Timer for publishing data
        self.timer = self.create_timer(1.0, self.publish_data)  # Publish at 1 Hz

    def publish_data(self):
        # Generate random sensor data
        analog_sensors = {
            "TP2": random.uniform(-0.032, 10.676),
            "TP3": random.uniform(0.73, 10.302),
            "H1": random.uniform(-0.036, 10.288),
            "DV_pressure": random.uniform(-0.032, 9.844),
            "Reservoirs": random.uniform(0.712, 10.3),
            "Oil_temperature": random.uniform(15.4, 89.05),
            "Motor_current": random.uniform(0.02, 9.295),
        }

        digital_sensors = {
            "COMP": random.randint(0, 1),
            "DV_eletric": random.randint(0, 1),
            "Towers": random.randint(0, 1),
            "MPG": random.randint(0, 1),
            "LPS": random.randint(0, 1),
            "Pressure_switch": random.randint(0, 1),
            "Oil_level": random.randint(0, 1),
            "Caudal_impulses": random.randint(0, 1),
        }

        # Publish analog sensor data
        self.tp2_pub.publish(Float32(data=analog_sensors["TP2"]))
        self.tp3_pub.publish(Float32(data=analog_sensors["TP3"]))
        self.h1_pub.publish(Float32(data=analog_sensors["H1"]))
        self.dv_pressure_pub.publish(Float32(data=analog_sensors["DV_pressure"]))
        self.reservoirs_pub.publish(Float32(data=analog_sensors["Reservoirs"]))
        self.oil_temperature_pub.publish(Float32(data=analog_sensors["Oil_temperature"]))
        self.motor_current_pub.publish(Float32(data=analog_sensors["Motor_current"]))

        # Publish digital sensor data
        self.comp_pub.publish(Int32(data=digital_sensors["COMP"]))
        self.dv_eletric_pub.publish(Int32(data=digital_sensors["DV_eletric"]))
        self.towers_pub.publish(Int32(data=digital_sensors["Towers"]))
        self.mpg_pub.publish(Int32(data=digital_sensors["MPG"]))
        self.lps_pub.publish(Int32(data=digital_sensors["LPS"]))
        self.pressure_switch_pub.publish(Int32(data=digital_sensors["Pressure_switch"]))
        self.oil_level_pub.publish(Int32(data=digital_sensors["Oil_level"]))
        self.caudal_impulses_pub.publish(Int32(data=digital_sensors["Caudal_impulses"]))

        self.get_logger().info("Train 1: Published sensor data.")


def main(args=None):
    rclpy.init(args=args)
    node = Train1SensorPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
