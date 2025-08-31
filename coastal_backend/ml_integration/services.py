import os
import pickle
import joblib
import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from django.db import models
from monitoring.models import CoastalLocation, SensorData, RiskAssessment, Alert
from .models import MLModel, PredictionLog

logger = logging.getLogger(__name__)


class MLPredictionService:
    """Service for integrating ML model predictions with coastal data"""
    
    def __init__(self):
        self.model = None
        self.model_version = None
        self.feature_columns = None
        self._load_model()
    
    def _load_model(self):
        """Load the ML model from file"""
        try:
            # Try to get the active model from database
            ml_model_record = MLModel.objects.filter(is_active=True).first()
            
            if ml_model_record:
                model_path = ml_model_record.model_file_path
                self.model_version = f"{ml_model_record.name}_v{ml_model_record.version}"
            else:
                # Fallback to default model path
                model_path = os.path.join(settings.ML_MODEL_PATH, 'coastal_risk_model.pkl')
                self.model_version = "default_v1.0"
            
            if os.path.exists(model_path):
                # Try loading with joblib first, then pickle
                try:
                    self.model = joblib.load(model_path)
                except:
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                
                logger.info(f"ML model loaded successfully: {self.model_version}")
                
                # Define expected feature columns (you may need to adjust this based on your model)
                self.feature_columns = [
                    'water_level', 'wave_height', 'wind_speed', 'wind_direction',
                    'air_pressure', 'water_temperature', 'hour_of_day', 'day_of_year'
                ]
            else:
                logger.warning(f"ML model not found at {model_path}. Using dummy predictions.")
                self.model = None
                
        except Exception as e:
            logger.error(f"Failed to load ML model: {str(e)}")
            self.model = None
    
    def prepare_features(self, location: CoastalLocation, hours_back: int = 6) -> Optional[pd.DataFrame]:
        """Prepare feature data from sensor readings for ML model input"""
        try:
            # Get recent sensor data
            since = timezone.now() - timedelta(hours=hours_back)
            sensor_data = location.sensor_data.filter(timestamp__gte=since)
            
            if not sensor_data.exists():
                logger.warning(f"No sensor data available for {location.name}")
                return None
            
            # Create a feature dictionary
            features = {}
            
            # Get latest values for each measurement type
            for measurement_type, _ in SensorData.MEASUREMENT_TYPES:
                latest = sensor_data.filter(measurement_type=measurement_type).first()
                if latest:
                    features[measurement_type] = latest.value
                else:
                    # Use default values for missing measurements
                    defaults = {
                        'water_level': 0.0,
                        'wave_height': 1.0,
                        'wind_speed': 5.0,
                        'wind_direction': 180.0,
                        'air_pressure': 1013.25,
                        'water_temperature': 15.0,
                        'salinity': 35.0
                    }
                    features[measurement_type] = defaults.get(measurement_type, 0.0)
            
            # Add temporal features
            now = timezone.now()
            features['hour_of_day'] = now.hour
            features['day_of_year'] = now.timetuple().tm_yday
            
            # Create DataFrame with the expected columns
            df = pd.DataFrame([features])
            
            # Ensure all required columns are present
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0.0
            
            # Select only the required columns in the correct order
            df = df[self.feature_columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing features for {location.name}: {str(e)}")
            return None
    
    def predict_risk(self, location: CoastalLocation) -> Optional[Dict]:
        """Generate risk prediction for a coastal location"""
        start_time = time.time()
        
        try:
            # Prepare feature data
            features = self.prepare_features(location)
            if features is None:
                return None
            
            if self.model is None:
                # Use dummy prediction if model is not available
                risk_score = np.random.uniform(0.1, 0.9)
                confidence = 0.5
                logger.warning(f"Using dummy prediction for {location.name}")
            else:
                # Make prediction using the loaded model
                prediction = self.model.predict_proba(features)[0]
                risk_score = float(prediction[1]) if len(prediction) > 1 else float(prediction[0])
                confidence = max(prediction)  # Use max probability as confidence
            
            # Determine risk level based on score
            if risk_score < 0.3:
                risk_level = 'low'
            elif risk_score < 0.6:
                risk_level = 'medium'
            elif risk_score < 0.8:
                risk_level = 'high'
            else:
                risk_level = 'critical'
            
            # Prepare prediction data
            prediction_data = {
                'input_features': features.to_dict('records')[0],
                'model_output': risk_score,
                'processing_timestamp': timezone.now().isoformat()
            }
            
            # Save risk assessment
            risk_assessment = RiskAssessment.objects.create(
                location=location,
                risk_score=risk_score,
                risk_level=risk_level,
                prediction_data=prediction_data,
                model_version=self.model_version,
                confidence=confidence
            )
            
            # Log the prediction
            PredictionLog.objects.create(
                model=MLModel.objects.filter(is_active=True).first(),
                location=location,
                input_data=prediction_data['input_features'],
                prediction_result={
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'confidence': confidence
                },
                execution_time=time.time() - start_time
            )
            
            # Check if alert should be triggered
            if risk_score >= settings.ALERT_THRESHOLD:
                self._trigger_alert(location, risk_assessment)
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'confidence': confidence,
                'assessment_id': risk_assessment.id
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk for {location.name}: {str(e)}")
            return None
    
    def _trigger_alert(self, location: CoastalLocation, risk_assessment: RiskAssessment):
        """Trigger an alert based on risk assessment"""
        try:
            # Determine alert type and severity based on risk level and input data
            alert_type = 'general'
            severity = 'warning'
            
            if risk_assessment.risk_level == 'critical':
                severity = 'critical'
            elif risk_assessment.risk_level == 'high':
                severity = 'urgent'
            
            # Check for specific conditions in the prediction data
            input_data = risk_assessment.prediction_data.get('input_features', {})
            
            if input_data.get('water_level', 0) > 5:
                alert_type = 'coastal_flooding'
                severity = 'critical'
            elif input_data.get('wave_height', 0) > 8:
                alert_type = 'high_waves'
            elif input_data.get('wind_speed', 0) > 25:
                alert_type = 'storm_surge'
            
            # Create alert message
            title = f"{alert_type.replace('_', ' ').title()} Alert - {location.name}"
            message = (
                f"High risk detected at {location.name}. "
                f"Risk Score: {risk_assessment.risk_score:.2f} "
                f"({risk_assessment.risk_level.upper()}). "
                f"Please review current conditions and take appropriate action."
            )
            
            # Check if there's already an active alert for this location
            existing_alert = Alert.objects.filter(
                location=location,
                status='active',
                alert_type=alert_type
            ).first()
            
            if not existing_alert:
                Alert.objects.create(
                    location=location,
                    risk_assessment=risk_assessment,
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    message=message
                )
                logger.info(f"Alert triggered for {location.name}: {title}")
            else:
                logger.info(f"Alert already exists for {location.name}, skipping duplicate")
                
        except Exception as e:
            logger.error(f"Error triggering alert for {location.name}: {str(e)}")
    
    def predict_all_locations(self):
        """Run risk predictions for all active locations"""
        locations = CoastalLocation.objects.filter(is_active=True)
        results = {}
        
        for location in locations:
            prediction = self.predict_risk(location)
            if prediction:
                results[location.station_id] = prediction
        
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the currently loaded model"""
        return {
            'version': self.model_version,
            'is_loaded': self.model is not None,
            'feature_columns': self.feature_columns,
            'alert_threshold': settings.ALERT_THRESHOLD
        }


class ModelPerformanceService:
    """Service for tracking and analyzing ML model performance"""
    
    @staticmethod
    def get_prediction_statistics(days_back: int = 7) -> Dict:
        """Get prediction statistics for the last N days"""
        since = timezone.now() - timedelta(days=days_back)
        
        predictions = PredictionLog.objects.filter(created_at__gte=since)
        
        if not predictions.exists():
            return {
                'total_predictions': 0,
                'average_execution_time': 0,
                'predictions_by_day': []
            }
        
        total_predictions = predictions.count()
        avg_execution_time = predictions.aggregate(
            avg_time=models.Avg('execution_time')
        )['avg_time'] or 0
        
        # Group by day
        predictions_by_day = []
        for i in range(days_back):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_predictions = predictions.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            predictions_by_day.append({
                'date': day_start.date().isoformat(),
                'count': day_predictions
            })
        
        return {
            'total_predictions': total_predictions,
            'average_execution_time': round(avg_execution_time, 4),
            'predictions_by_day': predictions_by_day
        }
    
    @staticmethod
    def get_alert_statistics(days_back: int = 7) -> Dict:
        """Get alert statistics for the last N days"""
        since = timezone.now() - timedelta(days=days_back)
        
        alerts = Alert.objects.filter(created_at__gte=since)
        
        if not alerts.exists():
            return {
                'total_alerts': 0,
                'alerts_by_severity': {},
                'alerts_by_type': {}
            }
        
        total_alerts = alerts.count()
        
        # Group by severity
        alerts_by_severity = {}
        for severity, _ in Alert.SEVERITY_LEVELS:
            count = alerts.filter(severity=severity).count()
            alerts_by_severity[severity] = count
        
        # Group by type
        alerts_by_type = {}
        for alert_type, _ in Alert.ALERT_TYPES:
            count = alerts.filter(alert_type=alert_type).count()
            alerts_by_type[alert_type] = count
        
        return {
            'total_alerts': total_alerts,
            'alerts_by_severity': alerts_by_severity,
            'alerts_by_type': alerts_by_type
        }
