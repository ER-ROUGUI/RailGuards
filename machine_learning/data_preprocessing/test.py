import joblib
import pandas as pd

# Load the saved model and scaler
model_regression = joblib.load('/home/ubuntu/railGuard/machine_learning/data_preprocessing/logistic_regression_model.pkl')
scaler = joblib.load('/home/ubuntu/railGuard/machine_learning/data_preprocessing/scaler.pkl')

# Define a function for prediction
def predict_new_data(new_data):
    # Ensure the new data is a DataFrame with the correct columns
    training_feature_names = [
        'timestamp', 'TP2', 'TP3', 'H1', 'DV_pressure', 'Reservoirs',
        'Oil_temperature', 'Motor_current', 'COMP', 'DV_eletric', 'Towers',
        'MPG', 'LPS', 'Pressure_switch', 'Oil_level', 'Caudal_impulses'
    ]
    new_df = pd.DataFrame(new_data)[training_feature_names]
    
    # Scale the new data using the pre-fitted scaler
    new_scaled = scaler.transform(new_df)
    
    # Predict the class and probability
    y_pred = model_regression.predict(new_scaled)
    y_pred_prob = model_regression.predict_proba(new_scaled)[:, 1]
    
    return y_pred, y_pred_prob

# Example new data
new_sample = {
    'timestamp': [150],  # Replace with realistic timestamp
    'TP2': [-0.018],
    'TP3': [8.248],
    'H1': [8.238],
    'DV_pressure': [-0.024],
    'Reservoirs': [8.248],
    'Oil_temperature': [49.450],
    'Motor_current': [0.0400],
    'COMP': [1.0],
    'DV_eletric': [0.0],
    'Towers': [1.0],
    'MPG': [1.0],
    'LPS': [0.0],
    'Pressure_switch': [1.0],
    'Oil_level': [1.0],
    'Caudal_impulses': [1.0]
}

# Predict for the new sample
class_labels = {0: "Not Failure", 1: "Failure"}

y_pred, y_pred_prob = predict_new_data(new_sample)

y_pred_label = [class_labels[label] for label in y_pred]

print(f"Prediction (Class): {y_pred_label}")
print(f"Probability of Failure: {y_pred_prob}")

