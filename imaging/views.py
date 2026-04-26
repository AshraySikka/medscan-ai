from django.shortcuts import render, redirect, get_list_or_404
from .models import Patient, Scan, Report
from .forms import PatientForm, ScanForm

# View for a quick dashboard
def dashboard(request):
    patients = Patient.objects.all().order_by('-created_at')
    scans = Scan.objects.all().order_by('-uploaded_at')[:5] # this will be loading the last 5 scans

    return render(request, 'imaging/dashboard.html', {
        'patients': patients,
        'scans':scans
    })

def upload_scan(request):
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        scan_form = ScanForm(request.POST, request.FILES) # request.FILES handles the image uploads
        if patient_form.is_valid() and scan_form.is_valid():
            patient = patient_form.save()
            scan = scan_form.save(commit=False) #this will not be saved to the db yet as we need to add patient details to the scan
            scan.patent = patient
            scan.save()
            return redirect('dashboard')
        
    else:
        patient_form = PatientForm()
        scan_form = ScanForm()

    return render(request, 'imaging/upload.html', {
        'patient_form': patient_form,
        'scan_form':scan_form
    })

