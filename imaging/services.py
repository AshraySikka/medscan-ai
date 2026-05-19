import anthropic
import base64
import json
import requests
from django.conf import settings

# initializing the Anthropic client using the API key from .env
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def get_image_mime_type_from_url(url):
    # detect mime type from the cloudinary URL extension
    url_lower = url.lower().split('?')[0]  # strip query params
    if url_lower.endswith('.png'):
        return 'image/png'
    elif url_lower.endswith('.webp'):
        return 'image/webp'
    elif url_lower.endswith('.gif'):
        return 'image/gif'
    else:
        return 'image/jpeg'  # default to jpeg

def get_image_mime_type(image_path):
    # read the first few bytes of the file to detect actual format
    # file extensions can lie, magic bytes don't
    with open(image_path, 'rb') as f:
        header = f.read(12)

    if header[:4] == b'\x89PNG':
        return 'image/png'
    elif header[:3] == b'GIF':
        return 'image/gif'
    elif header[:4] in (b'RIFF',) and header[8:12] == b'WEBP':
        return 'image/webp'
    elif header[:2] in (b'\xff\xd8',):
        return 'image/jpeg'
    else:
        # fall back to extension based detection if magic bytes don't match
        ext = image_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
        }
        return mime_types.get(ext, 'image/jpeg')

def encode_image_from_url(url):
    # fetch the image from cloudinary URL and encode to base64
    response = requests.get(url)
    return base64.b64encode(response.content).decode('utf-8')

def analyze_scan(scan):
    # check if image is a cloudinary URL or local file path
    image_url = scan.image

    if image_url and image_url.startswith('http'):
        # fetch from cloudinary URL
        image_data = encode_image_from_url(image_url)
        mime_type = get_image_mime_type_from_url(image_url)
    else:
        # fall back to local file path for development
        image_data = encode_image(image_url)
        mime_type = get_image_mime_type(image_url)

    # telling claude exactly what we need back and in what format
    prompt = f"""You are a radiology AI assistant. Analyze this {scan.get_scan_type_display()} image for patient: {scan.patient.name}, Age: {scan.patient.age}.

Return a JSON object ONLY with no backticks, no markdown, no preamble, using this exact structure:
{{
    "impression": "1-2 sentence overall impression",
    "findings": [
        {{
            "label": "short finding name",
            "detail": "one sentence detail",
            "severity": "normal|mild|moderate|severe"
        }}
    ],
    "recommendation": "brief recommendation sentence",
    "confidence": 87
}}

Be medically realistic and precise. Comment on all relevant anatomical structures visible in the image."""

    # sending the image and prompt to claude vision
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ]
    )

    # extracting the raw text response from claude
    raw_response = message.content[0].text

    # claude sometimes wraps response in backticks even when told not to, stripping just in case
    cleaned_response = raw_response.strip()
    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response.split('```')[1]
        if cleaned_response.startswith('json'):
            cleaned_response = cleaned_response[4:]
        cleaned_response = cleaned_response.strip()

    # parsing the JSON claude returned into a python dictionary
    findings_data = json.loads(cleaned_response)

    return raw_response, findings_data


def encode_image(image_path):
    # claude needs the image as base64 encoded string, not a file path
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')