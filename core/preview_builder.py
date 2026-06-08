import json
from pydantic import ValidationError
from models.schemas import AIResponseSchema

class PreviewBuilder:
    def __init__(self):
        pass
        
    def parse_ai_response(self, response_text: str) -> dict:
        """
        Parses the AI JSON response, validates it, and builds a tree structure.
        """
        try:
            # Find the JSON block if the AI returns extra text
            text = response_text.strip()
            if "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                text = text[start:end]
                
            data = json.loads(text)
            
            # Validate with Pydantic
            validated = AIResponseSchema(**data)
            
            # Build Tree
            # Structure: { "CategoryName": { "SubcategoryName": [file1, file2], "_files": [file3] } }
            tree = {}
            for file_item in validated.files:
                cat = file_item.category
                subcat = file_item.subcategory
                
                if cat not in tree:
                    tree[cat] = {"_files": []}
                    
                if subcat:
                    if subcat not in tree[cat]:
                        tree[cat][subcat] = []
                    tree[cat][subcat].append({
                        "path": file_item.path,
                        "confidence": file_item.confidence
                    })
                else:
                    tree[cat]["_files"].append({
                        "path": file_item.path,
                        "confidence": file_item.confidence
                    })
                    
            return tree
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from AI response: {e}")
        except ValidationError as e:
            raise ValueError(f"AI response failed schema validation: {e}")
