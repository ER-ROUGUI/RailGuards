from setuptools import find_packages, setup

package_name = 'sensors_simulator'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='saad',
    maintainer_email='saad.errougui@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "temperature_sensor = sensors_simulator.temperature_publisher:main",
            "ros_kafka = sensors_simulator.ros2_kafka_bridge:main",
            "vibration_sensor = sensors_simulator.vibration_publisher:main",
            "full_ros_kafka = sensors_simulator.full_ros2_kafka_bridge:main",
            "full_sensor = sensors_simulator.full_sensor_publisher:main"
            
        ],
    },
)
