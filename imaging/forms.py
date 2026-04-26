from django import forms 
from .models import Patient, Scan

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'mrn']

class ScanForm(forms.ModelForm):
    class Meta:
        model = Scan
        fields = ['scan_type', 'image']