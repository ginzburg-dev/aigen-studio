import os
import uuid
from aigen.core.constants import DEFAULT_ROLE
from aigen.core.chat_history import ChatHistory, CACHE_DIR
from aigen.core.prompt import Prompt
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Union

class ChatSession(ABC):
    """Chat session base class"""
    def __init__(self, *, default_role=DEFAULT_ROLE, session_id: Optional[str] = None) -> None:
        self.default_role = default_role
        self.session_id = session_id or str(uuid.uuid4())
        self.history = ChatHistory()
        self.buffer = self._create_buffer()
        self.buffer.role = self.default_role

    def get_session_id(self):
        return self.session_id
    
    def get_cache_filename(self, name: Optional[str] = None) -> str:
        filename = name or self.session_id
        file_path = "./cache/" + filename + ".yaml"
        return file_path
    
    def load_chat_history(self, name: str = None) -> None:
        path = self.get_cache_filename(name)
        self.history.load_from_yaml(path)

    def save_chat_history(self, name: str = None) -> None:
        path = self.get_cache_filename(name)
        self.history.save_to_yaml(path)

    def delete_cache_file(self, name: Optional[str] = None) -> None:
        file_path = self.get_cache_filename(name)
        if os.path.exists(file_path ):
            try:
                os.remove(file_path)
                print(f"File '{file_path}' deleted successfully!")
            except Exception as e:
                print(f"Error deleting file: {e}")

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

    @abstractmethod
    def chat(self) -> Any:
        ...

    @abstractmethod
    def _create_buffer(self) -> Any:
        """Subclasses must return a Prompt (or derived) instance."""
        ...

    def __del__(self) -> None:
        self.delete_cache_file()
