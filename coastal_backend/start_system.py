#!/usr/bin/env python
"""
Startup script for the coastal alarm system.
This script starts the Django development server and runs initial predictions.
"""

import os
import subprocess
import time
import requests
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coastal_backend.settings')
django.setup()

from monitoring.models import CoastalLocation
from ml_integration.services import MLPredictionService

def run_initial_predictions():
    """Run initial predictions for all locations"""
    print("Running initial risk predictions...")
    
    ml_service = MLPredictionService()
    locations = CoastalLocation.objects.filter(is_active=True)
    
    for location in locations:
        try:
            prediction = ml_service.predict_risk(location)
            if prediction:
                print(f"✓ {location.name}: Risk Level = {prediction['risk_level']}, Score = {prediction['risk_score']:.3f}")
            else:
                print(f"✗ {location.name}: Prediction failed")
        except Exception as e:
            print(f"✗ {location.name}: Error - {str(e)}")

def check_system_health():
    """Check if the system is running properly"""
    try:
        response = requests.get('http://localhost:8000/api/health/', timeout=5)
        if response.status_code == 200:
            print("✓ System health check passed")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except requests.RequestException:
        print("✗ Could not connect to server")
        return False

def main():
    print("=== Coastal Alarm System Startup ===")
    print("1. Running initial predictions...")
    
    try:
        run_initial_predictions()
        print("\n2. Starting Django development server...")
        print("Server will be available at: http://localhost:8000")
        print("\nAPI Endpoints:")
        print("- Dashboard: http://localhost:8000/api/dashboard/")
        print("- Locations: http://localhost:8000/api/locations/")
        print("- Sensor Data: http://localhost:8000/api/sensor-data/")
        print("- Alerts: http://localhost:8000/api/alerts/")
        print("- Health Check: http://localhost:8000/api/health/")
        print("\nAdmin Interface: http://localhost:8000/admin/")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the Django development server
        subprocess.run(['python', 'manage.py', 'runserver'])
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting system: {str(e)}")

if __name__ == "__main__":
    main()
