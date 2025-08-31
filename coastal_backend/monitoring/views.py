from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

from .models import CoastalLocation, SensorData, RiskAssessment, Alert, DataIngestionLog
from .serializers import (
    CoastalLocationSerializer, SensorDataSerializer, SensorDataCreateSerializer,
    RiskAssessmentSerializer, AlertSerializer, DashboardDataSerializer,
    LocationDetailSerializer
)
from .services import DataIngestionService, DataValidationService
from ml_integration.services import MLPredictionService


class CoastalLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for coastal location management"""
    queryset = CoastalLocation.objects.all()
    serializer_class = CoastalLocationSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LocationDetailSerializer
        return CoastalLocationSerializer
    
    @action(detail=True, methods=['post'])
    def run_prediction(self, request, pk=None):
        """Trigger ML prediction for a specific location"""
        location = self.get_object()
        ml_service = MLPredictionService()
        
        prediction = ml_service.predict_risk(location)
        if prediction:
            return Response({
                'status': 'success',
                'prediction': prediction
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Unable to generate prediction'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def sensor_data(self, request, pk=None):
        """Get sensor data for a specific location"""
        location = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        sensor_data = location.sensor_data.filter(timestamp__gte=since)
        
        serializer = SensorDataSerializer(sensor_data, many=True)
        return Response(serializer.data)


class SensorDataViewSet(viewsets.ModelViewSet):
    """ViewSet for sensor data management"""
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SensorDataCreateSerializer
        return SensorDataSerializer
    
    def get_queryset(self):
        queryset = SensorData.objects.all()
        
        # Filter by location if specified
        location_id = self.request.query_params.get('location')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        # Filter by measurement type if specified
        measurement_type = self.request.query_params.get('measurement_type')
        if measurement_type:
            queryset = queryset.filter(measurement_type=measurement_type)
        
        # Filter by time range
        hours = int(self.request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        queryset = queryset.filter(timestamp__gte=since)
        
        return queryset.order_by('-timestamp')
    
    def create(self, request, *args, **kwargs):
        """Create sensor data with validation"""
        # Validate the data before creating
        data = request.data
        
        # If it's a batch of data
        if isinstance(data, list):
            cleaned_data = DataValidationService.clean_sensor_data(data)
            serializer = self.get_serializer(data=cleaned_data, many=True)
        else:
            # Single data point
            if DataValidationService.validate_sensor_reading(
                data.get('measurement_type'),
                float(data.get('value', 0))
            ):
                serializer = self.get_serializer(data=data)
            else:
                return Response({
                    'error': 'Invalid sensor reading values'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RiskAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for risk assessment data (read-only)"""
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    
    def get_queryset(self):
        queryset = RiskAssessment.objects.all()
        
        # Filter by location if specified
        location_id = self.request.query_params.get('location')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        # Filter by risk level if specified
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filter by time range
        hours = int(self.request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        queryset = queryset.filter(created_at__gte=since)
        
        return queryset.order_by('-created_at')


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for alert management"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    
    def get_queryset(self):
        queryset = Alert.objects.all()
        
        # Filter by status if specified
        alert_status = self.request.query_params.get('status')
        if alert_status:
            queryset = queryset.filter(status=alert_status)
        
        # Filter by severity if specified
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by location if specified
        location_id = self.request.query_params.get('location')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.resolve()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active alerts"""
        active_alerts = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)


class DashboardView(APIView):
    """API view for dashboard overview data"""
    
    def get(self, request):
        """Get dashboard overview statistics"""
        # Get basic statistics
        total_locations = CoastalLocation.objects.filter(is_active=True).count()
        active_alerts = Alert.objects.filter(status='active').count()
        
        # Get high risk locations (risk score >= 0.7)
        high_risk_locations = RiskAssessment.objects.filter(
            risk_score__gte=0.7,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).values('location').distinct().count()
        
        # Get latest sensor data (last 10 readings)
        latest_sensor_data = SensorData.objects.all()[:10]
        
        # Get recent alerts (last 5)
        recent_alerts = Alert.objects.all()[:5]
        
        dashboard_data = {
            'total_locations': total_locations,
            'active_alerts': active_alerts,
            'high_risk_locations': high_risk_locations,
            'latest_sensor_data': SensorDataSerializer(latest_sensor_data, many=True).data,
            'recent_alerts': AlertSerializer(recent_alerts, many=True).data
        }
        
        serializer = DashboardDataSerializer(dashboard_data)
        return Response(serializer.data)


class DataIngestionView(APIView):
    """API view for triggering data ingestion"""
    
    def post(self, request):
        """Trigger manual data ingestion"""
        try:
            ingestion_service = DataIngestionService()
            ingestion_service.ingest_all_locations()
            
            # Run ML predictions after data ingestion
            ml_service = MLPredictionService()
            predictions = ml_service.predict_all_locations()
            
            return Response({
                'status': 'success',
                'message': 'Data ingestion completed',
                'predictions_generated': len(predictions)
            })
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Data ingestion failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Simple health check endpoint"""
    
    def get(self, request):
        """Return system health status"""
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })
