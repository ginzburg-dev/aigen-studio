import os
from pathlib import Path
import uuid
from abc import ABC, abstractmethod
from typing import Any

from aigen.file_handler import FileHandler
from aigen.client.llm import LLM
from aigen.config import AigenConfig


class Chat(ABC):
    """Chat session base class"""

    _config = AigenConfig()

    def __init__(self) -> None:
        self._id = str(uuid.uuid4())
        self._llm: LLM
        self._history: list[dict[str, Any]] = []

    @property
    def id(self):
        return self._id

    @property
    def llm(self) -> LLM:
        return self._llm
    
    @property
    def config(self) -> AigenConfig:
        return self._config
    
    @property
    def history(self) -> list[dict[str, Any]]:
        return self._history

    @property
    def chat_cache_dir(self) -> Path:
        return self.config.get_cache_dir() / self.id

    def _cache_filepath(self, name: str) -> Path:
        filename = name or self.id
        file_path = self.chat_cache_dir / f"{filename}.yaml"
        return file_path
    
    def load(self, name: str) -> None:
        _path = self._cache_filepath(name)
        self._history = FileHandler().read_yaml(_path)

    def save(self, name: str) -> None:
        _path = self._cache_filepath(name)
        FileHandler().write_yaml(_path, self.history)

    def set_prompt(self, prompt: Prompt, role: Optional[str] = None):
        """Set prompt manulally. Override a session's prompt buffer"""
        prompt.role = role or self.default_role
        self.buffer = prompt

    def _move_buffer_to_history(self):
        """Add prompt buffer to history"""
        if self.buffer.content:
            self.history.add(self.buffer)
            self.buffer.clear()

    def add_text(self, text: str, *, role: Optional[str] = None):
        self.buffer.role = role or self.buffer.role
        self.buffer.add_text(text)
        
    def add_image(self, image_path: str, *, detailed: bool = None, role: Optional[str] = None):
        self.buffer.role = role or self.buffer.role
        self.buffer.add_image(image_path=image_path, detailed=detailed)

    def add_prompt(self, prompt: Prompt):
        self._move_buffer_to_history()
        self.history.add(prompt)

    @abstractmethod
    def chat(self) -> Any:
        ...

    @abstractmethod
    def _create_buffer(self) -> Any:
        """Subclasses must return a Prompt (or derived) instance."""
        ...

    def __del__(self) -> None:
        self.delete_cache_file()
