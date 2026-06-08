import json
import requests
from typing import List, Dict
from providers.base_provider import BaseAIProvider
from providers.prompt_template import PROMPT_TEMPLATE

class OllamaProvider(BaseAIProvider):
    def __init__(self, model_name="llama3", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def classify_files(self, files_metadata: List[Dict]) -> str:
        prompt = PROMPT_TEMPLATE.replace("{FILES_METADATA}", json.dumps(files_metadata, indent=2))
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Force JSON output if supported
        }
        
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "")
