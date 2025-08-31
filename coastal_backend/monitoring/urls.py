from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'locations', views.CoastalLocationViewSet)
router.register(r'sensor-data', views.SensorDataViewSet)
router.register(r'risk-assessments', views.RiskAssessmentViewSet)
router.register(r'alerts', views.AlertViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/ingest-data/', views.DataIngestionView.as_view(), name='data-ingestion'),
    path('api/health/', views.HealthCheckView.as_view(), name='health-check'),
]
