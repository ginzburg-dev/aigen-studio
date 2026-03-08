from abc import ABC, abstractmethod
from typing import Any

from aigen.models import Role


class Prompt(ABC):
    """Builds prompts for text and images."""

    def __init__(self,
            role: str,
            *,
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

    @abstractmethod
    def add_text(self, text: str) -> None:
        ...

    @abstractmethod
    def add_image(self, image_path: str, detailed = True) -> None:
        ...

    def to_dict(self, type_filter: str | list[str] | None = None) -> list[dict[str, Any]]:
        """Compile prompt as a dict, optionally filtering by type."""
        if type_filter == None:
            return self._content
        allowed = {type_filter} if isinstance(type_filter, str) else set(type_filter)
        return [item for item in self._content if item.get("type") in allowed]

    def clear(self) -> None:
        self._role = Role.USER.value
        self._content = []

