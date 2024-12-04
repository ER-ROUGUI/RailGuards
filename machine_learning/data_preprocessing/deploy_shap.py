import json
import joblib
import numpy as np
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime, timedelta
import shap

# Load pre-trained model and scaler
model = joblib.load('/home/ubuntu/railGuard/machine_learning/data_preprocessing/xgb_model.pkl')  # Replace with your model file
scaler = joblib.load('/home/ubuntu/railGuard/machine_learning/data_preprocessing/scaler_xgb.pkl')  # Replace with your scaler file

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

# Feature names (ensure they match the model's training data)
feature_names = [
    'timestamp', 'TP2', 'TP3', 'H1', 'DV_pressure', 'Reservoirs',
    'Oil_temperature', 'Motor_current', 'COMP', 'DV_eletric',
    'Towers', 'MPG', 'LPS', 'Pressure_switch', 'Oil_level', 'Caudal_impulses'
]

# Cache to store historical data for threshold calculation
history_cache = []  # Store historical anomaly rates
cache_limit = 1000  # Maximum number of entries to keep in the cache

# Helper function: Preprocess incoming data
def preprocess_data(data):
    """
    Preprocess incoming data to match the model's expected input format.
    """
    # Convert timestamp to numerical value
    data['timestamp'] = (datetime.fromisoformat(data['timestamp'][:-6]) - datetime(2024, 1, 1)).total_seconds() / (24 * 3600)
    # Ensure data is in a DataFrame
    sample = pd.DataFrame([data], columns=feature_names)
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

# SHAP Explainer initialization
explainer = shap.TreeExplainer(model)

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

        # Store anomaly rate in the history cache
        if len(history_cache) >= cache_limit:
            history_cache.pop(0)  # Remove oldest entry to maintain cache size
        history_cache.append(anomaly)

        # Calculate anomaly rate over the history cache
        anomaly_rate = np.mean(history_cache)

        # Compute SHAP values for anomaly explanation
        shap_values = explainer.shap_values(sample_scaled)
        responsible_feature = feature_names[np.argmax(shap_values[0])]

        # Simulate future data using historical trends
        simulated_data = simulate_future_data(sample_df, steps=48)  # Simulate next 8 hours
        simulated_data_scaled = scaler.transform(simulated_data)

        # Predict anomalies on future data
        future_anomalies = model.predict(simulated_data_scaled)
        future_anomaly_rate = np.mean(future_anomalies)  # Average anomaly rate

        # Determine dynamic threshold (IQR-based)
        q1 = np.percentile(history_cache, 25)
        q3 = np.percentile(history_cache, 75)
        iqr = q3 - q1
        dynamic_threshold = q3 + 1.5 * iqr

        # Predict maintenance flag
        maintenance_flag = future_anomaly_rate > dynamic_threshold

        # Prepare and send prediction to Kafka
        prediction_message = {
            "timestamp": sensor_data['timestamp'],
            "current_anomaly": anomaly,
            "future_anomaly_rate": float(future_anomaly_rate),
            "maintenance_flag": int(maintenance_flag),
            "dynamic_threshold": float(dynamic_threshold),
            "anomaly_rate_last_cache": float(anomaly_rate),
            "responsible_feature": responsible_feature
        }
        producer.send('future_anomaly_predictions', prediction_message)

        print(f"Processed data: {sensor_data}, Prediction: {prediction_message}")

    except Exception as e:
        print(f"Error processing message: {e}")
