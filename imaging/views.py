from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient, Scan, Report
from .forms import PatientForm, ScanForm
from .services import analyze_scan

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

        if scan_form.is_valid():
            mrn = request.POST.get('mrn').strip()
            name = request.POST.get('name').strip()
            age = request.POST.get('age').strip()

            #get existing patient by MRN or create a new one
            patient, created = Patient.objects.get_or_create(
                mrn=mrn,
                defaults={'name':name, 'age':age}
            )

            scan = scan_form.save(commit=False) #this will not be saved to the db yet as we need to add patient details to the scan
            scan.patient = patient
            scan.save()

            # sending scan to claude and getting back raw response and parsed findings
            raw_response, findings_data = analyze_scan(scan)

            # saving the report to DB linked to this scan
            Report.objects.create(
                scan = scan,
                raw_response = raw_response,
                findings=findings_data,
                confidence=findings_data.get('confidence', 0)

            )

            # redirecting to report page for this scan
            return redirect('report', scan_id=scan.id)
        
    else:
        # this runs on GET request, just load empty forms
        patient_form = PatientForm()
        scan_form = ScanForm()

    return render(request, 'imaging/upload.html', {
        'patient_form': patient_form,
        'scan_form':scan_form
    })


def report(request, scan_id):
    # fetching scan and its related report, 404 if not found
    scan = get_object_or_404(Scan, id=scan_id)
    report = get_object_or_404(Report, scan=scan)
    return render(request, 'imaging/report.html', {
        'scan':scan,
        'report':report
    })
