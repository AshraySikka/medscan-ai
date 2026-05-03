import pytest
from imaging.models import Patient, Scan, Report

@pytest.mark.django_db
def test_patient_creation():
    #basic creation test, checks all fields save correctly
    patient = Patient.objects.create(
        name = "John Smith",
        age = 45,
        mrn = "MRN001"
    )

    assert patient.name == "John Smith"
    assert patient.age == 45
    assert patient.mrn == "MRN001"
    assert patient.created_at is not None


@pytest.mark.django_db
def test_patient_mrn_unique():
    #mrn must be unique, second patient with the same mrn should fail
    Patient.objects.create(
        name = "John Smith",
        age = 45,
        mrn = "MRN003"
    )
    with pytest.raises(Exception):
        Patient.objects.create(name="Another Person", age=30, mrn="MRN003")


@pytest.mark.django_db
def test_scan_str():
    #checks scan __str__ returns scan type and patient name
    patient = Patient.objects.create(
        name = "John Smith",
        age = 45,
        mrn = "MRN004"        
    )
    scan = Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )

    assert str(scan) == "Chest X-Ray - John Smith"


@pytest.mark.django_db
def test_scan_fk_to_patient():
    #checks the foreign key relationship works correctly
    patient = Patient.objects.create(
        name="John Smith",
        age = 45,
        mrn = "MRN005"
    )
    scan = Scan.objects.create(
        patient = patient,
        scan_type = "mri",
        image = "scans/test.jpg"
    )

    assert scan.patient.name == "John Smith"

@pytest.mark.django_db
def test_scan_deleted_when_patient_deleted():
    # cascade delete — scan should be gone when patient is deleted
    patient = Patient.objects.create(
        name="John Smith",
        age=45,
        mrn="MRN006"
    )
    scan = Scan.objects.create(
        patient=patient,
        scan_type="ct_scan",
        image="scans/test.jpg"
    )
    scan_id = scan.id
    patient.delete()
    assert Scan.objects.filter(id=scan_id).count() == 0

@pytest.mark.django_db
def test_report_str():
    # checks report __str__ references the scan correctly
    patient = Patient.objects.create(
        name="John Smith",
        age=45,
        mrn="MRN007"
    )
    scan = Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )
    report = Report.objects.create(
        scan=scan,
        raw_response='{"impression": "test"}',
        findings={"impression": "test", "findings": [], "recommendation": "none", "confidence": 90},
        confidence=90
    )
    assert "Chest X-Ray" in str(report)
    assert "John Smith" in str(report)

@pytest.mark.django_db
def test_report_one_to_one_scan():
    # a scan can only have one report, second one should fail
    patient = Patient.objects.create(
        name="John Smith",
        age=45,
        mrn="MRN008"
    )
    scan = Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )
    Report.objects.create(
        scan=scan,
        raw_response='{"impression": "test"}',
        findings={"impression": "test", "findings": [], "recommendation": "none", "confidence": 90},
        confidence=90
    )
    with pytest.raises(Exception):
        Report.objects.create(
            scan=scan,
            raw_response='{"impression": "test2"}',
            findings={"impression": "test2", "findings": [], "recommendation": "none", "confidence": 80},
            confidence=80
        )