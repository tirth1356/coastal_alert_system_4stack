from django.db import models
from monitoring.models import CoastalLocation


class MLModel(models.Model):
    """Model representing different ML models used for risk prediction"""
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    description = models.TextField()
    model_file_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class PredictionLog(models.Model):
    """Model for logging ML model predictions and performance"""
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    location = models.ForeignKey(CoastalLocation, on_delete=models.CASCADE)
    input_data = models.JSONField()
    prediction_result = models.JSONField()
    execution_time = models.FloatField()  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model.name} - {self.location.name}"
