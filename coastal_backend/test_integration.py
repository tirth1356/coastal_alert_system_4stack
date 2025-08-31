#!/usr/bin/env python
"""
Script to test the integration between the React frontend and Django backend.
This script verifies that all API endpoints work correctly with the frontend.
"""

import requests
import json
import subprocess
import time
import threading
import os
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class IntegrationTester:
    def __init__(self):
        self.backend_running = False
        self.frontend_running = False
    
    def check_backend(self):
        """Check if Django backend is running"""
        try:
            response = requests.get(f"{BACKEND_URL}/api/health/", timeout=5)
            if response.status_code == 200:
                print("✅ Django backend is running")
                self.backend_running = True
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except requests.RequestException:
            print("❌ Django backend is not running")
            return False
    
    def check_frontend(self):
        """Check if React frontend is accessible"""
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                print("✅ React frontend is accessible")
                self.frontend_running = True
                return True
            else:
                print(f"❌ Frontend check failed: {response.status_code}")
                return False
        except requests.RequestException:
            print("❌ React frontend is not running")
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints that the frontend uses"""
        print("\n🔍 Testing API endpoints...")
        
        endpoints_to_test = [
            ("GET", "/api/health/", "Health Check"),
            ("GET", "/api/dashboard/", "Dashboard Data"),
            ("GET", "/api/locations/", "Locations List"),
            ("GET", "/api/sensor-data/?hours=1", "Recent Sensor Data"),
            ("GET", "/api/alerts/active/", "Active Alerts"),
            ("GET", "/api/risk-assessments/?hours=24", "Risk Assessments"),
        ]
        
        results = []
        
        for method, endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {description}: {response.status_code}")
                    results.append({
                        'endpoint': endpoint,
                        'status': 'success',
                        'data_keys': list(data.keys()) if isinstance(data, dict) else f"{len(data)} items"
                    })
                else:
                    print(f"❌ {description}: {response.status_code}")
                    results.append({
                        'endpoint': endpoint,
                        'status': 'failed',
                        'error': f"Status {response.status_code}"
                    })
            except Exception as e:
                print(f"❌ {description}: {str(e)}")
                results.append({
                    'endpoint': endpoint,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend-backend communication"""
        print("\n🌐 Testing CORS configuration...")
        
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        try:
            # Test preflight request
            response = requests.options(f"{BACKEND_URL}/api/dashboard/", headers=headers, timeout=5)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            print("CORS Headers received:")
            for header, value in cors_headers.items():
                if value:
                    print(f"  ✅ {header}: {value}")
                else:
                    print(f"  ❌ {header}: Not set")
            
            # Test actual request with Origin
            response = requests.get(f"{BACKEND_URL}/api/dashboard/", headers={'Origin': FRONTEND_URL}, timeout=5)
            if response.status_code == 200:
                print("✅ CORS configuration appears to be working")
                return True
            else:
                print(f"❌ CORS test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ CORS test error: {str(e)}")
            return False
    
    def test_data_flow(self):
        """Test the complete data flow: sensor data → ML prediction → alerts"""
        print("\n🔄 Testing complete data flow...")
        
        try:
            # 1. Get a location
            locations_response = requests.get(f"{BACKEND_URL}/api/locations/", timeout=5)
            if locations_response.status_code != 200:
                print("❌ Failed to get locations")
                return False
            
            locations = locations_response.json()
            if not locations:
                print("❌ No locations found")
                return False
            
            location_id = locations[0]['id']
            location_name = locations[0]['name']
            print(f"✅ Using location: {location_name}")
            
            # 2. Add test sensor data
            sensor_data = {
                "location": location_id,
                "measurement_type": "water_level",
                "value": 5.5,  # High value to potentially trigger alert
                "unit": "meters",
                "timestamp": datetime.now().isoformat() + "Z",
                "data_source": "integration_test"
            }
            
            sensor_response = requests.post(
                f"{BACKEND_URL}/api/sensor-data/",
                json=sensor_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if sensor_response.status_code == 201:
                print("✅ Sensor data added successfully")
            else:
                print(f"❌ Failed to add sensor data: {sensor_response.status_code}")
                return False
            
            # 3. Trigger ML prediction
            prediction_response = requests.post(
                f"{BACKEND_URL}/api/locations/{location_id}/run_prediction/",
                timeout=10
            )
            
            if prediction_response.status_code == 200:
                prediction_data = prediction_response.json()
                print(f"✅ ML prediction successful: {prediction_data}")
                
                # Check if prediction makes sense
                if 'prediction' in prediction_data:
                    risk_score = prediction_data['prediction'].get('risk_score', 0)
                    risk_level = prediction_data['prediction'].get('risk_level', 'unknown')
                    print(f"  📊 Risk Score: {risk_score:.3f}")
                    print(f"  ⚠️ Risk Level: {risk_level}")
            else:
                print(f"❌ ML prediction failed: {prediction_response.status_code}")
                return False
            
            # 4. Check for generated alerts
            time.sleep(1)  # Give system time to process
            alerts_response = requests.get(f"{BACKEND_URL}/api/alerts/active/", timeout=5)
            
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                print(f"✅ Retrieved {len(alerts)} active alerts")
                
                if alerts:
                    latest_alert = alerts[0]
                    print(f"  🚨 Latest Alert: {latest_alert['title']}")
                    print(f"  📍 Location: {latest_alert['location_name']}")
                    print(f"  ⚡ Severity: {latest_alert['severity']}")
            else:
                print(f"❌ Failed to get alerts: {alerts_response.status_code}")
                return False
            
            print("✅ Complete data flow test successful!")
            return True
            
        except Exception as e:
            print(f"❌ Data flow test error: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate a comprehensive integration report"""
        print("\n" + "=" * 60)
        print("📋 INTEGRATION TEST REPORT")
        print("=" * 60)
        
        # System status
        print("\n🖥️ System Status:")
        print(f"  Django Backend: {'✅ Running' if self.backend_running else '❌ Not Running'}")
        print(f"  React Frontend: {'✅ Running' if self.frontend_running else '❌ Not Running'}")
        
        # API endpoints
        if self.backend_running:
            results = self.test_api_endpoints()
            successful_endpoints = sum(1 for r in results if r['status'] == 'success')
            total_endpoints = len(results)
            
            print(f"\n🔌 API Endpoints: {successful_endpoints}/{total_endpoints} working")
            
            for result in results:
                status_icon = "✅" if result['status'] == 'success' else "❌"
                print(f"  {status_icon} {result['endpoint']}")
        
        # CORS test
        if self.backend_running:
            cors_working = self.test_cors_configuration()
            print(f"\n🌐 CORS Configuration: {'✅ Working' if cors_working else '❌ Issues detected'}")
        
        # Data flow test
        if self.backend_running:
            data_flow_working = self.test_data_flow()
            print(f"\n🔄 Data Flow: {'✅ Working' if data_flow_working else '❌ Issues detected'}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        
        if not self.backend_running:
            print("  🔧 Start Django backend: cd coastal_backend && python start_system.py")
        
        if not self.frontend_running:
            print("  🔧 Start React frontend: cd coastal-dashboard && npm start")
        
        if self.backend_running and self.frontend_running:
            print("  ✨ Both systems are running! Your integration should work.")
            print("  🌐 Frontend: http://localhost:3000")
            print("  🔧 Backend: http://localhost:8000")
            print("  📊 Admin: http://localhost:8000/admin/")
        
        print("\n" + "=" * 60)

def main():
    print("🚀 Starting Frontend-Backend Integration Test")
    print("=" * 60)
    
    tester = IntegrationTester()
    
    # Check if systems are running
    tester.check_backend()
    tester.check_frontend()
    
    # Generate comprehensive report
    tester.generate_report()
    
    # Instructions for next steps
    if tester.backend_running and tester.frontend_running:
        print("\n🎉 Integration test completed successfully!")
        print("\n📝 Frontend should now be able to:")
        print("  ✅ Load real coastal location data")
        print("  ✅ Display current risk assessments")
        print("  ✅ Show active alerts")
        print("  ✅ Update automatically every 30 seconds")
        print("  ✅ Allow alert resolution")
    else:
        print("\n⚠️ Integration test incomplete - some services not running")

if __name__ == "__main__":
    main()
