from typing import List, Optional
from pydantic import BaseModel, Field

class FileClassification(BaseModel):
    path: str = Field(..., description="The full path or filename of the classified file")
    category: str = Field(..., description="The top-level category assigned to the file")
    subcategory: Optional[str] = Field(None, description="The subcategory assigned to the file, if any")
    confidence: int = Field(..., description="Confidence score from 0 to 100")

class AIResponseSchema(BaseModel):
    files: List[FileClassification] = Field(..., description="List of classified files")
