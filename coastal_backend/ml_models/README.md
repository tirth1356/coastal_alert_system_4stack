# ML Models Directory

This directory contains the trained machine learning models for coastal risk prediction.

## Expected Model Format

Your trained model should be saved as `coastal_risk_model.pkl` using either:
- `joblib.dump(model, 'coastal_risk_model.pkl')`
- `pickle.dump(model, open('coastal_risk_model.pkl', 'wb'))`

## Model Requirements

The model should:
1. Accept a pandas DataFrame with the following columns:
   - `water_level`: Water level in meters
   - `wave_height`: Wave height in meters  
   - `wind_speed`: Wind speed in m/s
   - `wind_direction`: Wind direction in degrees
   - `air_pressure`: Air pressure in mb
   - `water_temperature`: Water temperature in celsius
   - `hour_of_day`: Hour of the day (0-23)
   - `day_of_year`: Day of the year (1-365)

2. Return prediction probabilities using `predict_proba()` method
3. Output should be a binary classification (normal/risk) or risk score (0-1)

## Adding Your Model

1. Copy your trained model file to this directory
2. Update the model path in Django settings or via the admin interface
3. Ensure the model accepts the expected input format

## Example Model Training Script

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load your training data
# data = pd.read_csv('coastal_training_data.csv')

# Example training code (replace with your actual training logic)
# X = data[['water_level', 'wave_height', 'wind_speed', 'wind_direction', 'air_pressure', 'water_temperature', 'hour_of_day', 'day_of_year']]
# y = data['risk_label']  # 0 for normal, 1 for risk

# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X, y)

# Save the model
# joblib.dump(model, 'coastal_risk_model.pkl')
```
