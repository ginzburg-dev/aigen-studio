import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic_settings import BaseSettings

from aigen.config import AigenConfig

class LLM(ABC):
    """Base client for LLM interactions."""

    _config = AigenConfig()

    def __init__(self, model: str, max_tokens: int) -> None:
        self._model = model
        self._client = None
        self._max_tokens = max_tokens

    @property
    def model(self) -> str:
        return self._model

    @property
    def client(self) -> Any:
        return self._client

    @property
    def config(self) -> BaseSettings:
        return self._config

    @abstractmethod
    def generate(
        self, content: list[dict[str, Any]] | dict[str, Any] | str, **kwargs
    ) -> str | None:
        ...

