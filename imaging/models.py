from django.db import models
from django.core.files.storage import default_storage
import os
from datetime import date

class Patient(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    mrn = models.CharField(max_length=100, unique=True) # Medical Record Number
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): # Defining what this object will look like when called
        return f"{self.name} ({self.mrn})"


class Scan(models.Model):
    SCAN_TYPE = [
        ('chest_xray', 'Chest X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('bone_xray', 'Bone X-Ray'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scans')
    # storing cloudinary URL directly instead of using ImageField
    image = models.URLField(max_length=500, blank=True, null=True)
    scan_type = models.CharField(max_length=50, choices=SCAN_TYPE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_scan_type_display()} - {self.patient.name}" # pre-defined django method, can be used


class Report(models.Model):
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE, related_name='report') # one and only one connection
    raw_response = models.TextField()
    findings = models.JSONField()
    confidence = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.scan}"