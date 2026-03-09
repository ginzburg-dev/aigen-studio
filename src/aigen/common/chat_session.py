from pathlib import Path
import uuid
from typing import Any

from aigen.common.file_handler import FileHandler
from aigen.common.prompt import Prompt
from aigen.config import AigenConfig


class ChatSession:
    """Chat session base class."""

    _config = AigenConfig()

    def __init__(self, id: str | None = None) -> None:
        self._id = id if id else str(uuid.uuid4())
        self._history: list[dict[str, Any]] = []

    @property
    def id(self) -> str:
        """Unique identifier for this chat session."""
        return self._id

    @property
    def cache_dir_path(self) -> Path:
        """Path to the cache directory for this chat session."""
        return self._config.get_cache_dir() / self._id
    
    @property
    def history(self) -> list[dict[str, Any]]:
        """Chat history as a list of message dictionaries."""
        return self._history

    def set_history(self, history: list[dict[str, Any]]) -> None:
        """Set the chat history."""
        self._history = history

    def add_dict(self, message: dict[str, Any]) -> None:
        """Add a message dictionary to the chat history."""
        self._history.append(message)

    def add_prompt(self, prompt: Prompt) -> None:
        """Add a prompt to the chat history."""
        self._history.extend(prompt.to_dict())

    def load_from_file(self, file_path: str) -> None:
        """Load chat history from a file."""
        self._history = FileHandler.read_yaml(file_path)

    def save_to_file(self, file_path: str) -> None:
        """Save chat history to a file."""
        FileHandler.write_yaml(file_path, self._history)
