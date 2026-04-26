import anthropic 
import base64
import json
from django.conf import settings

# initializing the Anthropic client using the API key from .env
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def encode_image(image_path):
    # claude needs the image as base64 encoded string, not a file path
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_image_mime_type(image_path):
    # claude needs to know what kind of image it is receiving, the format basically
    ext = image_path.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',        
    }
    return mime_types.get(ext, 'image/jpeg') # default to 'jpeg' if unknown


def analyze_scan(scan):
    # build a full path to the image on disk
    image_path = scan.image.path

    image_data = encode_image(image_path)
    mime_type = get_image_mime_type(image_path)

    #telling claude exactly what we need back and in what format
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

    #sending the image and prompt to claude vision
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

    # claude sometimes wraps response in ```json ``` even when told not to, stripping it just in case
    cleaned_response = raw_response.strip()
    if cleaned_response.startswith('```'):
        cleaned_response = cleaned_response.split('```')[1]
        if cleaned_response.startswith('json'):
            cleaned_response = cleaned_response[4:]
        cleaned_response = cleaned_response.strip()

    # parsing the JSON claude returned into a python dictionary
    findings_data = json.loads(cleaned_response)

    return raw_response, findings_data