import pytest
from django.urls import reverse
from imaging.models import Patient, Scan, Report

pytestmark = pytest.mark.django_db

def test_dashboard_loads(client):
    #checks that dashboard returns 200
    response = client.get(reverse('dashboard'))
    assert response. status_code == 200

def test_upload_page_loads(client):
    #checks upload page returns 200 on GET
    response = client.get(reverse('upload_scan'))
    assert response.status_code == 200

def test_dashboard_shows_patients(client):
    # checks that patients created in db show up on dashboard
    Patient.objects.create(name="John Smith", age=45, mrn="MRN001")
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b"John Smith" in response.content

def test_patient_history_loads(client):
    # checks patient history page loads for a valid patient
    patient = Patient.objects.create(name="John Smith", age=45, mrn="MRN002")
    response = client.get(reverse('patient_history', args=[patient.id]))
    assert response.status_code == 200

def test_patient_history_404_for_invalid_patient(client):
    # checks that a non-existent patient returns 404
    response = client.get(reverse('patient_history', args=[99999]))
    assert response.status_code == 404

def test_report_page_loads(client):
    # checks report page loads correctly for a valid scan and report
    patient = Patient.objects.create(name="John Smith", age=45, mrn="MRN003")
    scan = Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )
    Report.objects.create(
        scan=scan,
        raw_response='{"impression": "test"}',
        findings={
            "impression": "Clear lungs",
            "findings": [],
            "recommendation": "No action needed",
            "confidence": 90
        },
        confidence=90
    )
    response = client.get(reverse('report', args=[scan.id]))
    assert response.status_code == 200

def test_report_404_for_invalid_scan(client):
    # checks that a non-existent scan returns 404
    response = client.get(reverse('report', args=[99999]))
    assert response.status_code == 404

def test_patient_history_shows_scans(client):
    # checks that scans show up on the patient history page
    patient = Patient.objects.create(name="Jane Doe", age=32, mrn="MRN004")
    Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )
    response = client.get(reverse('patient_history', args=[patient.id]))
    assert b"Chest X-Ray" in response.content
