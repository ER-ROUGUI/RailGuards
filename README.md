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
  [Apache Kafka Installation Guide]([https://kafka.apache.org/documentation/quickstart](https://hostman.com/tutorials/install-apache-kafka-on-ubuntu-22-04/)
- **Apache Spark**: Used for data processing.  
  [Apache Spark Installation Guide]([https://spark.apache.org/docs/latest/](https://phoenixnap.com/kb/install-spark-on-ubuntu)
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
```

 ```bash
 source ~/.bashrc
```

4. Run the sensor simulator:

```bash
  ros2 run sensors_simulator full_sensor_publisher
  ```

5. Verify the data:

List all ROS2 topics
```bash
ros2 topic list
```

Echo a topic, for example:

```bash
ros2 topic echo /Oil_temperature
```


## 3) Data Streaming

To set up Kafka for data streaming:

Install Kafka and unzip it into the directory ~/kafka.

Start the Kafka broker and Zookeeper:
```bash
~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties
```
In another terminal:
```bash
~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties
```

3. Verify Kafka is running:

Verify Kafka is running:

```bash
sudo systemctl status kafka
```

if not :

```bash
sudo systemctl start kafka
```
```bash
sudo systemctl enable kafka
```

4. Launch the ROS2-Kafka bridge to send sensor data to Kafka:
```bash
ros2 run sensors_simulator full_ros2_kafka_bridge
```

5. Listen to the Kafka topic (fulldata) to view sensor data being streamed:

```bash
~/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic fulldata
```

## 4) Data Processing with Spark
Sensor data contains noise and requires processing. To process data using Apache Spark:

1. Navigate to the data processing directory:
```bash
cd ~/railGuards/data_processing
```

2. Run the Spark job:
```bash
spark-submit --jars ~/spark_jars/<required-jar-files> full_spark_processing.py
```

# 3. Verify that the cleaned data is being written to the Kafka topic (cleaned_sensor_data) and InfluxDB.


## 5) Visualization with Grafana

To visualize the processed data:

Install and set up Grafana.
Connect Grafana to InfluxDB as a data source.
Import the provided Grafana dashboard JSON (~/railGuards/grafana/grafana_dashboard.json) file or manually create dashboards.
Use InfluxDB queries to visualize:
Sensor metrics (e.g., temperature, pressure).
Maintenance flags and anomaly rates from the Kafka topic future_anomaly_predictions.

# AI Predection

```bash
cd ~/railGuards/machine_learning/data_preprocessing/
```
then run :

```bash
python3 deployement.py
```

# Thank You









