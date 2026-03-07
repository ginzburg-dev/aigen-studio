from abc import ABC, abstractmethod
from typing import Any


class Prompt(ABC):
    """Builds prompts for text and images."""

    def __init__(self,
            role: str,
            text: str | None = None,
            image_path: str | None = None
    ) -> None:
        self._role: str = role
        self._content: list[dict[str, Any]] = []

        if text:
            self.add_text(text)
        if image_path:
            self.add_image(image_path)

    @property
    def role(self) -> str:
        return self._role
    
    @role.setter
    def role(self, value: str) -> None:
        self._role = value

    @property
    def content(self) -> list[dict[str, Any]]:
        return self._content

    @content.setter
    def content(self, value: list[dict[str, Any]]) -> None:
        self._content = value

    @abstractmethod
    def add_text(self, text: str) -> None:
        ...

    @abstractmethod
    def add_image(self, image_path: str, detailed = True) -> None:
        ...

    def clear(self) -> None:
        self._role = ""
        self._content = []

