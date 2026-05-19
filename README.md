# MedScan AI

AI-powered medical imaging analysis platform built with Django and Claude Vision API. Upload radiology images — X-rays, CT scans, MRIs — and get structured clinical reports generated instantly by Claude.

**Live demo:** https://medscan-ai-production-249d.up.railway.app

## What it does

- Upload medical images linked to a patient record
- Claude Vision analyzes the image and returns structured findings
- Reports include impression, per-finding severity, recommendation, and confidence score
- Patient history tracks all scans and reports over time
- Django admin panel for full data management

## Tech Stack

- Python 3.13
- Django 6.0
- PostgreSQL (production) / SQLite (local)
- Claude Vision API (claude-sonnet-4-5)
- Cloudinary (media storage)
- pytest + GitHub Actions CI
- HTML / CSS (no frontend framework)

## Local Setup

**1. Clone the repo**

````bash
git clone https://github.com/AshraySikka/medscan-ai.git
cd medscan-ai
````

**2. Create and activate virtual environment**

````bash
python3 -m venv venv
source venv/bin/activate
````

**3. Install dependencies**

````bash
pip install -r requirements.txt
````

**4. Add your environment variables**

````bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
````

**5. Run migrations**

````bash
python manage.py migrate
````

**6. Create an admin user**

````bash
python manage.py createsuperuser
````

**7. Start the server**

````bash
python manage.py runserver
````

Visit `http://localhost:8000` to use the app.
Visit `http://localhost:8000/admin` for the admin panel.

## Project Structure
