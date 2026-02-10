from django.db import models
from django.contrib.auth.models import User


class DatasetUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    total_count = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    equipment_distribution = models.JSONField()
    csv_file = models.FileField(upload_to='uploads/')
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.filename} - {self.upload_date}"


class EquipmentAlert(models.Model):
    """Store safety alerts for equipment"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    
    dataset = models.ForeignKey(DatasetUpload, on_delete=models.CASCADE, related_name='alerts')
    equipment_name = models.CharField(max_length=255)
    parameter = models.CharField(max_length=50)  # Flowrate, Pressure, Temperature
    value = models.FloatField()
    threshold = models.FloatField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.equipment_name} - {self.parameter}"


class AuditLog(models.Model):
    """Track all user actions for compliance"""
    ACTION_CHOICES = [
        ('UPLOAD', 'File Upload'),
        ('UPLOAD_FAILED', 'Upload Failed'),
        ('PDF_DOWNLOAD', 'PDF Downloaded'),
        ('VIEW', 'Data Viewed'),
        ('DELETE', 'Data Deleted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    dataset = models.ForeignKey(DatasetUpload, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"