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
    

def scan_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    patient_name = instance.patient.name.replace(' ','_').lower()
    scan_type = instance.scan_type
    today = date.today().strftime('%Y%m%d')
    base_filename = f"{patient_name}-{scan_type}-{today}"

    # will check if the file exits and increment
    counter = 1
    new_filename = f"{base_filename}.{ext}"

    while default_storage.exists(os.path.join('scans', new_filename)):
        new_filename = f"{base_filename}-{counter}.{ext}"
        counter += 1

    return os.path.join('scans', new_filename)

class Scan(models.Model):
    SCAN_TYPE = [
        ('chest_xray', 'Chest X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('bone_xray', 'Bone X-Ray'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scans')
    image = models.ImageField(upload_to=scan_upload_path)
    scan_type = models.CharField(max_length=50, choices=SCAN_TYPE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_scan_type_display()} - {self.patient.name}" # pre-defined django method, can be used
    

class Report(models.Model):
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE, related_name='report') # To make sure that we can have one and only one connection
    raw_response = models.TextField()
    findings = models.JSONField()
    confidence = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.scan}"