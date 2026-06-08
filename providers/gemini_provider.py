import json
import requests
from typing import List, Dict
from providers.base_provider import BaseAIProvider
from providers.prompt_template import PROMPT_TEMPLATE

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name="gemini-1.5-flash-latest"):
        self.api_key = api_key.strip() # Remove any trailing newlines or spaces
        self.model_name = model_name
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    def classify_files(self, files_metadata: List[Dict]) -> str:
        if not self.api_key:
            raise ValueError("Gemini API key is missing")

        prompt = PROMPT_TEMPLATE.replace("{FILES_METADATA}", json.dumps(files_metadata, indent=2))
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            error_details = response.text
            raise ValueError(f"API Error ({response.status_code}): {error_details}")
            
        response.raise_for_status()
        
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "{}"
