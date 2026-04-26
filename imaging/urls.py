from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard, name = 'dashboard'),
    path('upload/', views.upload_scan, name='upload_scan')
]
