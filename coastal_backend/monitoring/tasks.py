from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import DataIngestionService
from ml_integration.services import MLPredictionService
from .models import CoastalLocation, Alert, SensorData, RiskAssessment, DataIngestionLog

logger = logging.getLogger(__name__)


@shared_task
def ingest_coastal_data():
    """Celery task to ingest coastal data from external APIs"""
    try:
        logger.info("Starting coastal data ingestion task")
        
        ingestion_service = DataIngestionService()
        ingestion_service.ingest_all_locations()
        
        logger.info("Coastal data ingestion completed successfully")
        return "Data ingestion completed"
        
    except Exception as e:
        logger.error(f"Error in coastal data ingestion task: {str(e)}")
        raise


@shared_task
def run_risk_predictions():
    """Celery task to run ML risk predictions for all locations"""
    try:
        logger.info("Starting risk prediction task")
        
        ml_service = MLPredictionService()
        predictions = ml_service.predict_all_locations()
        
        logger.info(f"Risk predictions completed for {len(predictions)} locations")
        return f"Predictions generated for {len(predictions)} locations"
        
    except Exception as e:
        logger.error(f"Error in risk prediction task: {str(e)}")
        raise


@shared_task
def process_location_data(location_id):
    """Celery task to process data for a specific location"""
    try:
        location = CoastalLocation.objects.get(id=location_id)
        logger.info(f"Processing data for location: {location.name}")
        
        # First ingest latest data
        ingestion_service = DataIngestionService()
        noaa_records = ingestion_service.ingest_noaa_data(location)
        usgs_records = ingestion_service.ingest_usgs_data(location)
        
        # Then run prediction
        ml_service = MLPredictionService()
        prediction = ml_service.predict_risk(location)
        
        logger.info(
            f"Processing completed for {location.name}: "
            f"{noaa_records + usgs_records} records ingested, "
            f"prediction: {prediction}"
        )
        
        return {
            'location': location.name,
            'records_ingested': noaa_records + usgs_records,
            'prediction': prediction
        }
        
    except CoastalLocation.DoesNotExist:
        logger.error(f"Location with ID {location_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error processing location {location_id}: {str(e)}")
        raise


@shared_task
def cleanup_old_data():
    """Celery task to clean up old sensor data and logs"""
    try:
        logger.info("Starting data cleanup task")
        
        # Keep sensor data for 30 days
        sensor_cutoff = timezone.now() - timedelta(days=30)
        deleted_sensor_count = SensorData.objects.filter(
            created_at__lt=sensor_cutoff
        ).delete()[0]
        
        # Keep risk assessments for 90 days
        risk_cutoff = timezone.now() - timedelta(days=90)
        deleted_risk_count = RiskAssessment.objects.filter(
            created_at__lt=risk_cutoff
        ).delete()[0]
        
        # Keep resolved alerts for 30 days
        alert_cutoff = timezone.now() - timedelta(days=30)
        deleted_alert_count = Alert.objects.filter(
            status='resolved',
            resolved_at__lt=alert_cutoff
        ).delete()[0]
        
        # Keep ingestion logs for 7 days
        log_cutoff = timezone.now() - timedelta(days=7)
        deleted_log_count = DataIngestionLog.objects.filter(
            created_at__lt=log_cutoff
        ).delete()[0]
        
        logger.info(
            f"Data cleanup completed: "
            f"{deleted_sensor_count} sensor records, "
            f"{deleted_risk_count} risk assessments, "
            f"{deleted_alert_count} alerts, "
            f"{deleted_log_count} logs deleted"
        )
        
        return {
            'sensor_records_deleted': deleted_sensor_count,
            'risk_assessments_deleted': deleted_risk_count,
            'alerts_deleted': deleted_alert_count,
            'logs_deleted': deleted_log_count
        }
        
    except Exception as e:
        logger.error(f"Error in data cleanup task: {str(e)}")
        raise


@shared_task
def check_system_health():
    """Celery task to check system health and generate alerts if needed"""
    try:
        logger.info("Starting system health check")
        
        issues = []
        
        # Check if data ingestion is working (recent data within last 2 hours)
        recent_cutoff = timezone.now() - timedelta(hours=2)
        recent_data_count = SensorData.objects.filter(created_at__gte=recent_cutoff).count()
        
        if recent_data_count == 0:
            issues.append("No recent sensor data ingested")
        
        # Check for stuck alerts (active for more than 24 hours)
        stuck_alert_cutoff = timezone.now() - timedelta(hours=24)
        stuck_alerts = Alert.objects.filter(
            status='active',
            created_at__lt=stuck_alert_cutoff
        ).count()
        
        if stuck_alerts > 0:
            issues.append(f"{stuck_alerts} alerts have been active for more than 24 hours")
        
        # Check for locations without recent data
        locations_without_data = []
        for location in CoastalLocation.objects.filter(is_active=True):
            if not location.sensor_data.filter(created_at__gte=recent_cutoff).exists():
                locations_without_data.append(location.name)
        
        if locations_without_data:
            issues.append(f"No recent data for locations: {', '.join(locations_without_data)}")
        
        if issues:
            logger.warning(f"System health issues detected: {'; '.join(issues)}")
        else:
            logger.info("System health check passed")
        
        return {
            'status': 'healthy' if not issues else 'warning',
            'issues': issues,
            'recent_data_count': recent_data_count,
            'stuck_alerts': stuck_alerts
        }
        
    except Exception as e:
        logger.error(f"Error in system health check: {str(e)}")
        raise
