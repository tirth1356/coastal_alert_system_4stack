from rest_framework import serializers
from .models import CoastalLocation, SensorData, RiskAssessment, Alert, DataIngestionLog


class CoastalLocationSerializer(serializers.ModelSerializer):
    latest_risk_score = serializers.SerializerMethodField()
    active_alerts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CoastalLocation
        fields = '__all__'
    
    def get_latest_risk_score(self, obj):
        latest_assessment = obj.risk_assessments.first()
        return latest_assessment.risk_score if latest_assessment else None
    
    def get_active_alerts_count(self, obj):
        return obj.alerts.filter(status='active').count()


class SensorDataSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = SensorData
        fields = '__all__'


class SensorDataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sensor data via API"""
    
    class Meta:
        model = SensorData
        fields = ['location', 'measurement_type', 'value', 'unit', 'timestamp', 'data_source', 'quality_flag']


class RiskAssessmentSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = RiskAssessment
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    risk_score = serializers.FloatField(source='risk_assessment.risk_score', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard overview data"""
    total_locations = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    high_risk_locations = serializers.IntegerField()
    latest_sensor_data = serializers.ListField(child=serializers.DictField())
    recent_alerts = serializers.ListField(child=serializers.DictField())


class LocationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual location with related data"""
    recent_sensor_data = serializers.SerializerMethodField()
    latest_risk_assessment = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()
    
    class Meta:
        model = CoastalLocation
        fields = '__all__'
    
    def get_recent_sensor_data(self, obj):
        recent_data = obj.sensor_data.all()[:10]  # Last 10 readings
        return SensorDataSerializer(recent_data, many=True).data
    
    def get_latest_risk_assessment(self, obj):
        latest = obj.risk_assessments.first()
        return RiskAssessmentSerializer(latest).data if latest else None
    
    def get_active_alerts(self, obj):
        active_alerts = obj.alerts.filter(status='active')
        return AlertSerializer(active_alerts, many=True).data
