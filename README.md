# RailGuard: Morocco High Speed Train Hackathon Project

Hello everyone! This project was developed by **Aya Harrak**, **Oumama Lemaoukni**, and **Er-Rougui Saad** as part of the Morocco High Speed Train Hackathon.

This README provides the steps to execute the codes included in this project.

---

## 1) System Requirements

To run this project, ensure you have the following:

- **Operating System**: Ubuntu 22.04
- **ROS2**: Used for fake sensor data publishing.  
  [Installation Guide for ROS2 on Ubuntu](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)
- **Kafka**: Used for real-time data streaming.  
  [Apache Kafka Installation Guide](https://kafka.apache.org/documentation/quickstart)
- **Apache Spark**: Used for data processing.  
  [Apache Spark Installation Guide](https://spark.apache.org/docs/latest/)
- **Dependencies for Spark**:  
  Download necessary dependencies (`--jars` files) and place them in the directory `~/spark_jars`.
- **Grafana**: Used for data visualization and dashboards.  
  [Grafana Installation Guide](https://grafana.com/docs/grafana/latest/setup-grafana/installation/)

---

## 2) Sensors Publisher

To set up the ROS2-based sensor simulation:

1. Navigate to the RailGuards ROS2 workspace:
   ```bash
   cd ~/railGuards/ros2

2. Build the ROS2 package:
 ```bash
 colcon build --symlink-install

2. Source the ROS2 workspace by adding it to your bash configuration:
 ```bash
 echo "source ~/railGuards/ros2/install/setup.bash" >> ~/.bashrc
 ```bash
 source ~/.bashrc

4. Run the sensor simulator:

```bash
  ros2 run sensors_simulator full_sensor_publisher














