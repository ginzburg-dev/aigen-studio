import os
import copy
from aigen.core.prompt import Prompt
from aigen.core.file_handler import FileHandler
from typing import Any, Optional, List, Dict, Union

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class ChatHistory:
    """Handles chat history storage and retrival."""
    def __init__(self) -> None:
        self.data: List[Dict] = []

    def load_from_yaml(self, path: str = None) -> None:
        self.clear()
        self.data = FileHandler.read_yaml(path)
        
    def save_to_yaml(self, path: str) -> None:
        FileHandler.write_yaml(path, self.data)

    def add(self, obj: Union[Prompt, dict, List[Union[Prompt, dict]]]) -> None:
        if obj is None:
            return
        # Normalize to list for simpler logic
        items = obj if isinstance(obj, (list, tuple)) else [obj]
        for item in items:
            if isinstance(item, Prompt):
                self.data.append(item.to_dict())
            elif isinstance(item, dict):
                self.data.append(item)
            else:
                raise TypeError("Item must be a Prompt or dict")
    
    def clear(self) -> None:
        self.data.clear()

    def print(self) -> None:
        for item in self.data:
            print(item)
