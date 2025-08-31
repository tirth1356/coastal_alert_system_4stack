from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class CoastalLocation(models.Model):
    """Model representing a coastal monitoring location"""
    name = models.CharField(max_length=200)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    station_id = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.station_id})"


class SensorData(models.Model):
    """Model for storing real-time sensor data from coastal locations"""
    MEASUREMENT_TYPES = [
        ('water_level', 'Water Level'),
        ('wave_height', 'Wave Height'),
        ('wind_speed', 'Wind Speed'),
        ('wind_direction', 'Wind Direction'),
        ('air_pressure', 'Air Pressure'),
        ('water_temperature', 'Water Temperature'),
        ('salinity', 'Salinity'),
    ]

    location = models.ForeignKey(CoastalLocation, on_delete=models.CASCADE, related_name='sensor_data')
    measurement_type = models.CharField(max_length=20, choices=MEASUREMENT_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    data_source = models.CharField(max_length=50)  # e.g., 'NOAA', 'USGS', 'manual'
    quality_flag = models.CharField(max_length=10, default='good')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['location', 'measurement_type', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.location.name} - {self.measurement_type}: {self.value} {self.unit}"


class RiskAssessment(models.Model):
    """Model for storing ML model risk predictions"""
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    location = models.ForeignKey(CoastalLocation, on_delete=models.CASCADE, related_name='risk_assessments')
    risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    prediction_data = models.JSONField()  # Store the input data used for prediction
    model_version = models.CharField(max_length=50)
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location', '-created_at']),
            models.Index(fields=['risk_level', '-created_at']),
        ]

    def __str__(self):
        return f"{self.location.name} - {self.risk_level} ({self.risk_score:.2f})"


class Alert(models.Model):
    """Model for storing alert notifications"""
    ALERT_TYPES = [
        ('storm_surge', 'Storm Surge'),
        ('high_waves', 'High Waves'),
        ('coastal_flooding', 'Coastal Flooding'),
        ('erosion', 'Coastal Erosion'),
        ('water_quality', 'Water Quality Issue'),
        ('general', 'General Alert'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    location = models.ForeignKey(CoastalLocation, on_delete=models.CASCADE, related_name='alerts')
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location', 'status', '-created_at']),
            models.Index(fields=['severity', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location.name} ({self.severity})"

    def resolve(self):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class DataIngestionLog(models.Model):
    """Model for tracking data ingestion from external APIs"""
    source = models.CharField(max_length=50)  # e.g., 'NOAA', 'USGS'
    endpoint = models.URLField()
    status = models.CharField(max_length=20)  # 'success', 'error', 'partial'
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    execution_time = models.FloatField()  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source} - {self.status} ({self.records_processed} records)"
