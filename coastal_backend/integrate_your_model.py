#!/usr/bin/env python
"""
Helper script to integrate your actual ML model into the coastal alarm system.
This script helps you test and validate your model integration.
"""

import os
import django
import pandas as pd
import joblib
import pickle
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coastal_backend.settings')
django.setup()

from ml_integration.models import MLModel
from ml_integration.services import MLPredictionService
from monitoring.models import CoastalLocation

def test_model_loading(model_path):
    """Test if a model can be loaded successfully"""
    try:
        # Try joblib first
        try:
            model = joblib.load(model_path)
            print(f"✓ Model loaded successfully with joblib")
        except:
            # Try pickle
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print(f"✓ Model loaded successfully with pickle")
        
        # Check if model has predict_proba method
        if hasattr(model, 'predict_proba'):
            print("✓ Model has predict_proba method")
        else:
            print("✗ Model missing predict_proba method")
            return False
        
        return model
    except Exception as e:
        print(f"✗ Failed to load model: {str(e)}")
        return None

def test_model_prediction(model):
    """Test model prediction with sample data"""
    try:
        # Create test features
        test_features = pd.DataFrame([{
            'water_level': 2.5,
            'wave_height': 1.8,
            'wind_speed': 10.0,
            'wind_direction': 180.0,
            'air_pressure': 1015.0,
            'water_temperature': 22.0,
            'hour_of_day': 14,
            'day_of_year': 200
        }])
        
        # Test prediction
        prediction = model.predict_proba(test_features)
        print(f"✓ Model prediction successful: {prediction}")
        
        # Check prediction format
        if len(prediction) > 0 and len(prediction[0]) >= 1:
            risk_score = float(prediction[0][1]) if len(prediction[0]) > 1 else float(prediction[0][0])
            print(f"✓ Risk score extracted: {risk_score:.3f}")
            return True
        else:
            print("✗ Unexpected prediction format")
            return False
            
    except Exception as e:
        print(f"✗ Model prediction failed: {str(e)}")
        return False

def register_model_in_db(model_path, name, version, description):
    """Register the model in the database"""
    try:
        # Deactivate existing models
        MLModel.objects.filter(is_active=True).update(is_active=False)
        
        # Create new model record
        ml_model = MLModel.objects.create(
            name=name,
            version=version,
            description=description,
            model_file_path=model_path,
            is_active=True
        )
        print(f"✓ Model registered in database: {ml_model}")
        return ml_model
    except Exception as e:
        print(f"✗ Failed to register model: {str(e)}")
        return None

def test_full_integration():
    """Test the full ML integration pipeline"""
    try:
        print("\\nTesting full ML integration...")
        
        # Initialize ML service
        ml_service = MLPredictionService()
        
        # Test with a location
        location = CoastalLocation.objects.first()
        if not location:
            print("✗ No locations found. Run 'python manage.py seed_data' first.")
            return False
        
        print(f"Testing prediction for: {location.name}")
        
        # Run prediction
        prediction = ml_service.predict_risk(location)
        
        if prediction:
            print(f"✓ Full integration test successful!")
            print(f"  Risk Level: {prediction['risk_level']}")
            print(f"  Risk Score: {prediction['risk_score']:.3f}")
            print(f"  Confidence: {prediction['confidence']:.3f}")
            return True
        else:
            print("✗ Full integration test failed")
            return False
            
    except Exception as e:
        print(f"✗ Integration test error: {str(e)}")
        return False

def main():
    print("=== ML Model Integration Helper ===")
    print()
    
    # Get model path from user
    model_path = input("Enter the path to your ML model file (or press Enter for default): ").strip()
    
    if not model_path:
        model_path = "ml_models/coastal_risk_model.pkl"
        print(f"Using default path: {model_path}")
    
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"✗ Model file not found: {model_path}")
        print("Please provide the correct path to your model file.")
        return
    
    print(f"\\nTesting model: {model_path}")
    print("-" * 40)
    
    # Test model loading
    model = test_model_loading(model_path)
    if not model:
        return
    
    # Test model prediction
    if not test_model_prediction(model):
        return
    
    # Register model in database
    print("\\nRegistering model in database...")
    name = input("Model name (default: Your Coastal Risk Model): ").strip() or "Your Coastal Risk Model"
    version = input("Model version (default: 1.0): ").strip() or "1.0"
    description = input("Model description: ").strip() or "Custom coastal risk prediction model"
    
    ml_model_record = register_model_in_db(model_path, name, version, description)
    if not ml_model_record:
        return
    
    # Test full integration
    if test_full_integration():
        print("\\n" + "=" * 50)
        print("🎉 MODEL INTEGRATION SUCCESSFUL! 🎉")
        print("=" * 50)
        print("\\nYour model is now integrated and ready to use.")
        print("\\nNext steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Test the API endpoints")
        print("3. Connect your frontend dashboard")
        print("4. Set up Celery for background processing (optional)")
    else:
        print("\\n❌ Integration failed. Please check the errors above.")

if __name__ == "__main__":
    main()
