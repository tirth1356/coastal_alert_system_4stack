from django.contrib import admin
from .models import CoastalLocation, SensorData, RiskAssessment, Alert, DataIngestionLog


@admin.register(CoastalLocation)
class CoastalLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'station_id', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'station_id', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'measurement_type', 'value', 'unit', 'timestamp', 'data_source']
    list_filter = ['measurement_type', 'data_source', 'quality_flag', 'created_at']
    search_fields = ['location__name', 'measurement_type']
    readonly_fields = ['created_at']
    date_hierarchy = 'timestamp'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['location', 'risk_level', 'risk_score', 'confidence', 'model_version', 'created_at']
    list_filter = ['risk_level', 'model_version', 'created_at']
    search_fields = ['location__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'alert_type', 'severity', 'status', 'created_at']
    list_filter = ['alert_type', 'severity', 'status', 'created_at']
    search_fields = ['title', 'message', 'location__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    actions = ['resolve_alerts']
    
    def resolve_alerts(self, request, queryset):
        for alert in queryset:
            alert.resolve()
        self.message_user(request, f"Resolved {queryset.count()} alerts.")
    resolve_alerts.short_description = "Resolve selected alerts"


@admin.register(DataIngestionLog)
class DataIngestionLogAdmin(admin.ModelAdmin):
    list_display = ['source', 'status', 'records_processed', 'execution_time', 'created_at']
    list_filter = ['source', 'status', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
