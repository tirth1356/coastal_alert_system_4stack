import requests
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import List, Dict, Optional
import logging

from .models import CoastalLocation, SensorData, DataIngestionLog

logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting real-time coastal data from external APIs"""
    
    def __init__(self):
        self.apis = settings.COASTAL_DATA_APIS
    
    def ingest_all_locations(self):
        """Ingest data for all active coastal locations"""
        locations = CoastalLocation.objects.filter(is_active=True)
        
        for location in locations:
            try:
                # Ingest from NOAA
                self.ingest_noaa_data(location)
                # Ingest from USGS (if applicable)
                self.ingest_usgs_data(location)
            except Exception as e:
                logger.error(f"Error ingesting data for {location.name}: {str(e)}")
    
    def ingest_noaa_data(self, location: CoastalLocation):
        """Ingest data from NOAA Tides and Currents API"""
        start_time = time.time()
        records_processed = 0
        error_message = ""
        
        try:
            # NOAA API parameters
            base_url = self.apis['NOAA']['BASE_URL']
            
            # Get water level data
            water_level_params = {
                'begin_date': (timezone.now() - timedelta(hours=1)).strftime('%Y%m%d %H:%M'),
                'end_date': timezone.now().strftime('%Y%m%d %H:%M'),
                'station': location.station_id,
                'product': 'water_level',
                'datum': 'MLLW',
                'units': 'metric',
                'time_zone': 'gmt',
                'format': 'json'
            }
            
            response = requests.get(base_url, params=water_level_params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for reading in data['data']:
                        sensor_data = SensorData.objects.create(
                            location=location,
                            measurement_type='water_level',
                            value=float(reading['v']),
                            unit='meters',
                            timestamp=datetime.strptime(reading['t'], '%Y-%m-%d %H:%M'),
                            data_source='NOAA',
                            quality_flag=reading.get('q', 'good')
                        )
                        records_processed += 1
            
            # Get meteorological data
            met_params = {
                'begin_date': (timezone.now() - timedelta(hours=1)).strftime('%Y%m%d %H:%M'),
                'end_date': timezone.now().strftime('%Y%m%d %H:%M'),
                'station': location.station_id,
                'product': 'meteorological',
                'units': 'metric',
                'time_zone': 'gmt',
                'format': 'json'
            }
            
            met_response = requests.get(base_url, params=met_params, timeout=30)
            
            if met_response.status_code == 200:
                met_data = met_response.json()
                if 'data' in met_data:
                    for reading in met_data['data']:
                        # Wind speed
                        if 's' in reading and reading['s']:
                            SensorData.objects.create(
                                location=location,
                                measurement_type='wind_speed',
                                value=float(reading['s']),
                                unit='m/s',
                                timestamp=datetime.strptime(reading['t'], '%Y-%m-%d %H:%M'),
                                data_source='NOAA'
                            )
                            records_processed += 1
                        
                        # Wind direction
                        if 'd' in reading and reading['d']:
                            SensorData.objects.create(
                                location=location,
                                measurement_type='wind_direction',
                                value=float(reading['d']),
                                unit='degrees',
                                timestamp=datetime.strptime(reading['t'], '%Y-%m-%d %H:%M'),
                                data_source='NOAA'
                            )
                            records_processed += 1
                        
                        # Air pressure
                        if 'p' in reading and reading['p']:
                            SensorData.objects.create(
                                location=location,
                                measurement_type='air_pressure',
                                value=float(reading['p']),
                                unit='mb',
                                timestamp=datetime.strptime(reading['t'], '%Y-%m-%d %H:%M'),
                                data_source='NOAA'
                            )
                            records_processed += 1
            
            status = 'success'
        
        except requests.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            status = 'error'
            logger.error(f"NOAA API error for {location.name}: {error_message}")
        
        except Exception as e:
            error_message = f"Data processing error: {str(e)}"
            status = 'error'
            logger.error(f"NOAA processing error for {location.name}: {error_message}")
        
        # Log the ingestion attempt
        DataIngestionLog.objects.create(
            source='NOAA',
            endpoint=base_url,
            status=status,
            records_processed=records_processed,
            error_message=error_message,
            execution_time=time.time() - start_time
        )
        
        return records_processed
    
    def ingest_usgs_data(self, location: CoastalLocation):
        """Ingest data from USGS Water Services API"""
        start_time = time.time()
        records_processed = 0
        error_message = ""
        
        try:
            base_url = self.apis['USGS']['BASE_URL']
            
            # USGS parameters for water data
            params = {
                'format': 'json',
                'sites': location.station_id,
                'period': 'PT1H',  # Last 1 hour
                'parameterCd': '00065,00060',  # Water level and discharge
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'value' in data and 'timeSeries' in data['value']:
                    for series in data['value']['timeSeries']:
                        parameter_code = series['variable']['variableCode'][0]['value']
                        unit = series['variable']['unit']['unitCode']
                        
                        measurement_type = 'water_level' if parameter_code == '00065' else 'discharge'
                        
                        for value_data in series['values'][0]['value']:
                            if value_data['value'] != '-999999':  # Filter out no-data values
                                SensorData.objects.create(
                                    location=location,
                                    measurement_type=measurement_type,
                                    value=float(value_data['value']),
                                    unit=unit,
                                    timestamp=datetime.fromisoformat(value_data['dateTime'].replace('Z', '+00:00')),
                                    data_source='USGS'
                                )
                                records_processed += 1
            
            status = 'success'
        
        except requests.RequestException as e:
            error_message = f"API request failed: {str(e)}"
            status = 'error'
            logger.error(f"USGS API error for {location.name}: {error_message}")
        
        except Exception as e:
            error_message = f"Data processing error: {str(e)}"
            status = 'error'
            logger.error(f"USGS processing error for {location.name}: {error_message}")
        
        # Log the ingestion attempt
        DataIngestionLog.objects.create(
            source='USGS',
            endpoint=base_url,
            status=status,
            records_processed=records_processed,
            error_message=error_message,
            execution_time=time.time() - start_time
        )
        
        return records_processed
    
    def get_latest_sensor_data(self, location: CoastalLocation, hours: int = 24) -> Dict:
        """Get the latest sensor data for a location within specified hours"""
        since = timezone.now() - timedelta(hours=hours)
        
        data = {}
        for measurement_type, _ in SensorData.MEASUREMENT_TYPES:
            latest = location.sensor_data.filter(
                measurement_type=measurement_type,
                timestamp__gte=since
            ).first()
            
            if latest:
                data[measurement_type] = {
                    'value': latest.value,
                    'unit': latest.unit,
                    'timestamp': latest.timestamp,
                    'source': latest.data_source
                }
        
        return data


class DataValidationService:
    """Service for validating and cleaning incoming sensor data"""
    
    # Define reasonable ranges for different measurement types
    VALIDATION_RANGES = {
        'water_level': {'min': -10, 'max': 20},  # meters
        'wave_height': {'min': 0, 'max': 30},    # meters
        'wind_speed': {'min': 0, 'max': 100},    # m/s
        'wind_direction': {'min': 0, 'max': 360}, # degrees
        'air_pressure': {'min': 900, 'max': 1100}, # mb
        'water_temperature': {'min': -5, 'max': 40}, # celsius
        'salinity': {'min': 0, 'max': 40},       # ppt
    }
    
    @classmethod
    def validate_sensor_reading(cls, measurement_type: str, value: float) -> bool:
        """Validate if a sensor reading is within reasonable bounds"""
        if measurement_type not in cls.VALIDATION_RANGES:
            return True  # Allow unknown measurement types
        
        range_config = cls.VALIDATION_RANGES[measurement_type]
        return range_config['min'] <= value <= range_config['max']
    
    @classmethod
    def clean_sensor_data(cls, data: List[Dict]) -> List[Dict]:
        """Clean and validate a list of sensor data readings"""
        cleaned_data = []
        
        for reading in data:
            measurement_type = reading.get('measurement_type')
            value = reading.get('value')
            
            if measurement_type and value is not None:
                if cls.validate_sensor_reading(measurement_type, float(value)):
                    cleaned_data.append(reading)
                else:
                    logger.warning(
                        f"Invalid sensor reading filtered out: {measurement_type}={value}"
                    )
        
        return cleaned_data
