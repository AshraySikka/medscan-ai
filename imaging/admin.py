from django.contrib import admin
from .models import Patient, Scan, Report

# registering models so they show up in the admin panel
admin.site.register(Patient)
admin.site.register(Scan)
admin.site.register(Report)