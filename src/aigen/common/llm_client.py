from abc import ABC, abstractmethod
from typing import Any

from pydantic_settings import BaseSettings

from aigen.config import AigenConfig


class LLMClient(ABC):
    """Base client for LLM interactions."""

    _config = AigenConfig()

    def __init__(
        self, *, model: str | None = None, max_tokens: int | None = None
    ) -> None:
        self._model: str | None = model
        self._client: Any | None = None
        self._max_tokens: int | None = max_tokens

    @property
    def model(self) -> str | None:
        return self._model

    @property
    def config(self) -> BaseSettings:
        return self._config

    @abstractmethod
    def generate(
        self, content: list[dict[str, Any]] | dict[str, Any] | str, **kwargs
    ) -> str | None: ...
