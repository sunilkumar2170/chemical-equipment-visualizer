from rest_framework import serializers
from .models import DatasetUpload, EquipmentAlert, AuditLog


class DatasetUploadSerializer(serializers.ModelSerializer):
    alert_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DatasetUpload
        fields = '__all__'
        read_only_fields = ['user', 'upload_date']
    
    def get_alert_count(self, obj):
        return obj.alerts.count()


class EquipmentAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentAlert
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    dataset_name = serializers.CharField(source='dataset.filename', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'