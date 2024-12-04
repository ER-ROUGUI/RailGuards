import json
import joblib
import numpy as np
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime, timedelta

# Load pre-trained model and scaler
model = joblib.load('xgb_model.pkl')  # Replace with your model file
scaler = joblib.load('scaler_xgb.pkl')  # Replace with your scaler file

# Kafka Consumer for incoming sensor data
consumer = KafkaConsumer(
    'cleaned_sensor_data',  # Topic name for incoming data
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Kafka Producer for anomaly predictions
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Time window for predicting future anomalies
time_window = timedelta(hours=8)  # 8-hour prediction window

# Helper function: Preprocess incoming data
def preprocess_data(data):
    """
    Preprocess incoming data to match the model's expected input format.
    """
    feature_order = [
        'timestamp', 'TP2', 'TP3', 'H1', 'DV_pressure', 'Reservoirs',
        'Oil_temperature', 'Motor_current', 'COMP', 'DV_eletric',
        'Towers', 'MPG', 'LPS', 'Pressure_switch', 'Oil_level', 'Caudal_impulses'
    ]
    # Convert timestamp to numerical value
    data['timestamp'] = (datetime.fromisoformat(data['timestamp'][:-6]) - datetime(2024, 1, 1)).total_seconds() / (24 * 3600)
    # Ensure data is in a DataFrame
    sample = pd.DataFrame([data], columns=feature_order)
    return sample

# Helper function: Simulate future data
def simulate_future_data(current_data, steps=48):
    """
    Generate synthetic future data based on current trends.
    """
    future_data = []
    for _ in range(steps):  # 48 steps for 10-minute intervals
        # Generate synthetic data by adding small noise
        future_sample = current_data.mean() + np.random.normal(0, 0.1, size=current_data.shape[1])
        future_data.append(future_sample)
    return pd.DataFrame(future_data, columns=current_data.columns)

# Real-time data processing loop
for message in consumer:
    try:
        # Parse the incoming sensor data
        sensor_data = message.value
        sample_df = preprocess_data(sensor_data)
        sample_scaled = scaler.transform(sample_df)

        # Predict current anomaly
        prediction = model.predict(sample_scaled)
        anomaly = int(prediction[0])  # 1 = Failure, 0 = Normal

        # Simulate future data using historical trends
        simulated_data = simulate_future_data(sample_df, steps=48)  # Simulate next 8 hours
        simulated_data_scaled = scaler.transform(simulated_data)

        # Predict anomalies on future data
        future_anomalies = model.predict(simulated_data_scaled)
        anomaly_rate = np.mean(future_anomalies)  # Average anomaly rate

        # Determine dynamic threshold (IQR-based)
        q1 = np.percentile(future_anomalies, 25)
        q3 = np.percentile(future_anomalies, 75)
        iqr = q3 - q1
        dynamic_threshold = q3 + 3 * iqr   # based on https://ieeexplore-ieee-org.ezproxy.universite-paris-saclay.fr/stamp/stamp.jsp?tp=&arnumber=9564181

        # Predict maintenance flag
        maintenance_flag = anomaly_rate > dynamic_threshold

        # Prepare and send prediction to Kafka
        prediction_message = {
            "timestamp": sensor_data['timestamp'],
            "current_anomaly": anomaly,
            "future_anomaly_rate": float(anomaly_rate),
            "maintenance_flag": int(maintenance_flag),
            "dynamic_threshold": float(dynamic_threshold)
        }
        producer.send('future_anomaly_predictions', prediction_message)

        print(f"Processed data: {sensor_data}, Prediction: {prediction_message}")

    except Exception as e:
        print(f"Error processing message: {e}")
