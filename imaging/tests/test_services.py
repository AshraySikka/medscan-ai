import pytest
import json
from unittest.mock import MagicMock, patch, PropertyMock
from imaging.models import Patient, Scan
from imaging.services import analyze_scan, get_image_mime_type

pytestmark = pytest.mark.django_db

def test_get_image_mime_type_jpeg(tmp_path):
    # creates a real jpeg file with correct magic bytes
    f = tmp_path / "test.jpg"
    f.write_bytes(b'\xff\xd8\xff' + b'0' * 100)
    assert get_image_mime_type(str(f)) == "image/jpeg"

def test_get_image_mime_type_png(tmp_path):
    # creates a real png file with correct magic bytes
    f = tmp_path / "test.png"
    f.write_bytes(b'\x89PNG' + b'0' * 100)
    assert get_image_mime_type(str(f)) == "image/png"

def test_get_image_mime_type_webp(tmp_path):
    # creates a real webp file with correct magic bytes
    f = tmp_path / "test.webp"
    f.write_bytes(b'RIFF' + b'0' * 4 + b'WEBP' + b'0' * 100)
    assert get_image_mime_type(str(f)) == "image/webp"

def test_get_image_mime_type_unknown_defaults_to_jpeg(tmp_path):
    # unknown magic bytes should fall back to extension, xyz not in dict so defaults to jpeg
    f = tmp_path / "test.xyz"
    f.write_bytes(b'\x00\x00\x00\x00' + b'0' * 100)
    assert get_image_mime_type(str(f)) == "image/jpeg"

def test_analyze_scan_returns_raw_and_parsed(tmp_path):
    # creates a real fake image file
    fake_image = tmp_path / "test.jpg"
    fake_image.write_bytes(b'\xff\xd8\xff' + b'0' * 100)

    patient = Patient.objects.create(name="John Smith", age=45, mrn="MRN100")
    scan = Scan.objects.create(
        patient=patient,
        scan_type="chest_xray",
        image="scans/test.jpg"
    )

    fake_findings = {
        "impression": "Clear lung fields bilaterally.",
        "findings": [
            {"label": "Lung fields", "detail": "Clear bilaterally.", "severity": "normal"}
        ],
        "recommendation": "No action needed.",
        "confidence": 92
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(fake_findings))]

    # mocking scan.image.path to return our temp file path
    # bypasses django's media folder security check
    with patch('imaging.services.client.messages.create', return_value=mock_message):
        with patch.object(type(scan.image), 'path', new_callable=PropertyMock, return_value=str(fake_image)):
            raw_response, findings_data = analyze_scan(scan)

    assert isinstance(raw_response, str)
    assert findings_data['impression'] == "Clear lung fields bilaterally."
    assert findings_data['confidence'] == 92
    assert len(findings_data['findings']) == 1

def test_analyze_scan_confidence_score(tmp_path):
    fake_image = tmp_path / "test.jpg"
    fake_image.write_bytes(b'\xff\xd8\xff' + b'0' * 100)

    patient = Patient.objects.create(name="Jane Doe", age=32, mrn="MRN101")
    scan = Scan.objects.create(
        patient=patient,
        scan_type="mri",
        image="scans/test.jpg"
    )

    fake_findings = {
        "impression": "Normal MRI.",
        "findings": [],
        "recommendation": "Routine follow-up.",
        "confidence": 88
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(fake_findings))]

    with patch('imaging.services.client.messages.create', return_value=mock_message):
        with patch.object(type(scan.image), 'path', new_callable=PropertyMock, return_value=str(fake_image)):
            raw_response, findings_data = analyze_scan(scan)

    assert findings_data['confidence'] == 88

def test_analyze_scan_strips_markdown_backticks(tmp_path):
    # checks that markdown code fences are stripped from claude response
    fake_image = tmp_path / "test.jpg"
    fake_image.write_bytes(b'\xff\xd8\xff' + b'0' * 100)

    patient = Patient.objects.create(name="Bob Jones", age=55, mrn="MRN102")
    scan = Scan.objects.create(
        patient=patient,
        scan_type="ct_scan",
        image="scans/test.jpg"
    )

    fake_findings = {
        "impression": "Normal CT.",
        "findings": [],
        "recommendation": "No action.",
        "confidence": 85
    }

    # wrapping in backticks to simulate claude misbehaving
    wrapped_response = f"```json\n{json.dumps(fake_findings)}\n```"

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=wrapped_response)]

    with patch('imaging.services.client.messages.create', return_value=mock_message):
        with patch.object(type(scan.image), 'path', new_callable=PropertyMock, return_value=str(fake_image)):
            raw_response, findings_data = analyze_scan(scan)

    assert findings_data['impression'] == "Normal CT."
    assert findings_data['confidence'] == 85