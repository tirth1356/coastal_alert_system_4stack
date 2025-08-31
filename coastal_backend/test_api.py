#!/usr/bin/env python
"""
Script to test the coastal alarm system API endpoints.
Run this after starting the Django server to verify everything works.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint and print results"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\\n{description}")
    print(f"{method} {url}")
    print("-" * 50)
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Connection Error: {str(e)}")
        return None

def main():
    print("=== Coastal Alarm System API Tests ===")
    
    # Test health check
    test_endpoint("GET", "/health/", description="1. Health Check")
    
    # Test dashboard
    dashboard_data = test_endpoint("GET", "/dashboard/", description="2. Dashboard Overview")
    
    # Test locations
    locations = test_endpoint("GET", "/locations/", description="3. Get All Locations")
    
    if locations and len(locations) > 0:
        location_id = locations[0]['id']
        
        # Test specific location
        test_endpoint("GET", f"/locations/{location_id}/", description="4. Get Location Details")
        
        # Test sensor data for location
        test_endpoint("GET", f"/locations/{location_id}/sensor_data/?hours=1", 
                     description="5. Get Recent Sensor Data")
        
        # Test manual prediction
        test_endpoint("POST", f"/locations/{location_id}/run_prediction/", 
                     description="6. Trigger Manual Prediction")
    
    # Test recent sensor data
    test_endpoint("GET", "/sensor-data/?hours=2", description="7. Get Recent Sensor Data (All)")
    
    # Test risk assessments
    test_endpoint("GET", "/risk-assessments/?hours=24", description="8. Get Risk Assessments")
    
    # Test alerts
    test_endpoint("GET", "/alerts/", description="9. Get All Alerts")
    test_endpoint("GET", "/alerts/active/", description="10. Get Active Alerts")
    
    # Test adding new sensor data
    if locations and len(locations) > 0:
        sensor_data = {
            "location": locations[0]['id'],
            "measurement_type": "water_level",
            "value": 3.2,
            "unit": "meters",
            "timestamp": datetime.now().isoformat() + "Z",
            "data_source": "api_test"
        }
        
        test_endpoint("POST", "/sensor-data/", data=sensor_data, 
                     description="11. Add New Sensor Data")
    
    # Test data ingestion trigger
    test_endpoint("POST", "/ingest-data/", description="12. Trigger Data Ingestion")
    
    print("\\n" + "=" * 50)
    print("API Testing Completed!")
    print("=" * 50)
    print("\\nIf all tests passed, your backend is ready for frontend integration.")

if __name__ == "__main__":
    main()
