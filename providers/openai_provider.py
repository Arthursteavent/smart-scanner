import json
import requests
from typing import List, Dict
from providers.base_provider import BaseAIProvider
from providers.prompt_template import PROMPT_TEMPLATE

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name="gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def classify_files(self, files_metadata: List[Dict]) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing")

        prompt = PROMPT_TEMPLATE.replace("{FILES_METADATA}", json.dumps(files_metadata, indent=2))
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful file organization AI."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
