from abc import ABC, abstractmethod
from typing import List, Dict

class BaseAIProvider(ABC):
    @abstractmethod
    def classify_files(self, files_metadata: List[Dict]) -> str:
        """
        Takes a list of file metadata dictionaries, sends them to the AI,
        and returns a JSON string representing the AIResponseSchema.
        """
        pass
