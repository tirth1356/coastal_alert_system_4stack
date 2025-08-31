#!/usr/bin/env python
"""
Script to create a dummy ML model for testing the coastal alarm system.
This creates a simple Random Forest model that can be used for testing.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coastal_backend.settings')
django.setup()

def create_dummy_model():
    """Create a dummy ML model for testing purposes"""
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 1000
    
    # Feature columns that match what the ML service expects
    feature_columns = [
        'water_level', 'wave_height', 'wind_speed', 'wind_direction',
        'air_pressure', 'water_temperature', 'hour_of_day', 'day_of_year'
    ]
    
    # Generate realistic synthetic data
    data = {
        'water_level': np.random.normal(2.0, 1.5, n_samples),  # meters
        'wave_height': np.random.exponential(2.0, n_samples),  # meters  
        'wind_speed': np.random.exponential(8.0, n_samples),   # m/s
        'wind_direction': np.random.uniform(0, 360, n_samples), # degrees
        'air_pressure': np.random.normal(1013, 15, n_samples), # mb
        'water_temperature': np.random.normal(20, 5, n_samples), # celsius
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_year': np.random.randint(1, 366, n_samples)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create synthetic risk labels based on conditions
    # High risk if multiple danger conditions are met
    risk_conditions = (
        (df['water_level'] > 4) |  # High water level
        (df['wave_height'] > 5) |  # High waves
        ((df['wind_speed'] > 20) & (df['air_pressure'] < 1000)) |  # Storm conditions
        (df['water_temperature'] > 30)  # Unusual temperature
    )
    
    # Add some randomness to make it more realistic
    risk_probability = risk_conditions.astype(float) * 0.7 + np.random.uniform(0, 0.3, n_samples)
    y = (risk_probability > 0.5).astype(int)
    
    # Split the data
    X = df[feature_columns]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train the model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Test the model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Model training score: {train_score:.3f}")
    print(f"Model test score: {test_score:.3f}")
    
    # Save the model
    model_dir = 'ml_models'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'coastal_risk_model.pkl')
    
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # Test the model with sample data
    sample_features = pd.DataFrame([{
        'water_level': 3.5,
        'wave_height': 2.0,
        'wind_speed': 12.0,
        'wind_direction': 180.0,
        'air_pressure': 1010.0,
        'water_temperature': 22.0,
        'hour_of_day': 14,
        'day_of_year': 200
    }])
    
    prediction = model.predict_proba(sample_features)[0]
    print(f"Sample prediction: {prediction}")
    
    return model

if __name__ == "__main__":
    print("Creating dummy ML model for coastal risk prediction...")
    model = create_dummy_model()
    print("Dummy model created successfully!")
