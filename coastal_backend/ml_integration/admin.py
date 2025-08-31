from django.contrib import admin
from .models import MLModel, PredictionLog


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'version', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ['model', 'location', 'execution_time', 'created_at']
    list_filter = ['model', 'created_at']
    search_fields = ['location__name', 'model__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
