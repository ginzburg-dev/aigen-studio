from aigen.core.constants import DEFAULT_ROLE
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Union

class Prompt(ABC):
    """Builds prompts for text and images."""
    def __init__(
            self,
            *,
            role: Optional[str] = DEFAULT_ROLE, 
            text: Optional[str] = None, 
            image_path: Optional[str] = None
    ) -> None:
        self.role: str = role
        self.content: List[Dict[str,Any]] = []
        if text is not None:
            self.add_text(text)
        if image_path is not None:
            self.add_image(image_path)

    @abstractmethod
    def add_text(self, text: str) -> None:
        ...

    @abstractmethod
    def add_image(self, image_path, detailed = False):
        ...

    @abstractmethod
    def to_dict(self, role: Optional[str] = None, type_filter: Union[str, List[str], None] = None) -> Dict[str, Any]:
        ...
    
    def from_dict(self, data: dict) -> None:
        role = data.get("role")
        if role:
            self.role = role
        content = data.get("content")
        if content:
            self.content= content

    @abstractmethod
    def clear(self) -> None:
        ...

    def print(self) -> None:
        print(f"role: {self.role}")
        print(f"content: {self.content}")
