from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard, name = 'dashboard'),
    path('upload/', views.upload_scan, name='upload_scan'),
    path('report/<int:scan_id>/', views.report, name='report'),  #dynamic URL, scan id passed in
    path('patient/<int:patient_id>/', views.patient_history, name='patient_history'),
]
