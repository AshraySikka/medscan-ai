# MedScan AI

AI-powered medical imaging analysis platform built with Django and Claude Vision API. Upload radiology images: X-rays, CT scans, MRIs and get structured clinical reports generated instantly by Claude.

## What it does

- Upload medical images linked to a patient record
- Claude Vision analyzes the image and returns structured findings
- Reports include impression, per-finding severity, recommendation, and confidence score
- Patient history tracks all scans and reports over time
- Django admin panel for full data management

## Tech Stack

- Python 3.13
- Django 6.0
- SQLite
- Claude Vision API (claude-sonnet-4-5)
- Pillow
- HTML / CSS (no frontend framework)

## Local Setup

**1. Clone the repo**

```bash
git clone https://github.com/AshraySikka/medscan-ai.git
cd medscan-ai
```

**2. Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your Anthropic API key**

```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

**5. Run migrations**

```bash
python manage.py migrate
```

**6. Create an admin user**

```bash
python manage.py createsuperuser
```

**7. Start the server**

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to use the app.
Visit `http://localhost:8000/admin` for the admin panel.

## Project Structure

    medscan-ai/
    ├── medscan/              # project config, settings, root urls
    ├── imaging/              # main app
    │   ├── models.py         # Patient, Scan, Report models
    │   ├── views.py          # dashboard, upload, report, patient history
    │   ├── services.py       # Claude Vision API integration
    │   ├── forms.py          # PatientForm, ScanForm
    │   ├── urls.py           # app-level URL routing
    │   ├── admin.py          # admin panel registration
    │   ├── static/           # CSS
    │   └── templates/        # HTML templates
    ├── media/                # uploaded scan images (gitignored)
    ├── requirements.txt
    └── .env                  # API key (gitignored)


## How the AI analysis works

1. User uploads an image and fills in patient info
2. Django saves the image to disk using a clean naming convention: `patient_name-scan_type-date.ext`
3. `services.py` reads the image, encodes it to base64, and detects the true MIME type from magic bytes
4. The image and a structured prompt are sent to Claude Vision API
5. Claude returns a JSON report with impression, findings, severity levels, recommendation, and confidence score
6. The report is saved to the database and displayed on the report page

## Supported Image Types

JPEG, PNG, WebP, GIF

## Disclaimer

This application is for demonstration purposes only. AI-generated reports are not intended for clinical decision-making and should not replace qualified radiologist review.

## Author

Ashray Sikka · [github.com/AshraySikka](https://github.com/AshraySikka) · [linkedin.com/in/ashraysikka](https://linkedin.com/in/ashraysikka)
