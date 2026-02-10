from django.contrib import admin
from .models import DatasetUpload, EquipmentAlert, AuditLog

@admin.register(DatasetUpload)
class DatasetUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'upload_date', 'total_count']
    list_filter = ['upload_date', 'user']
    search_fields = ['filename']

@admin.register(EquipmentAlert)
class EquipmentAlertAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'parameter', 'severity', 'created_at']
    list_filter = ['severity', 'parameter', 'created_at']
    search_fields = ['equipment_name', 'message']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'details']