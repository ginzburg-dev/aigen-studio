import re
import time
from typing import Any

from aigen.common.llm_client import LLMClient
from aigen.constants import MAX_TOKENS
from aigen.models import GPTModel, Role, TemperaturePresets

import structlog
from openai import OpenAI, RateLimitError
from openai.types import Model
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionAssistantMessageParam,
)

LOGGER = structlog.get_logger(__name__)


class OpenAIClient(LLMClient):
    def __init__(
        self, *, model: str | None = None, max_tokens: int | None = None
    ) -> None:
        super().__init__(model=model, max_tokens=max_tokens)
        self._client = OpenAI(api_key=getattr(self.config, "openai_api_key"))

    def list_models(self) -> list[Model]:
        models = self._client.models.list().data if self._client else []
        return [m for m in models]

    def _format_message(self, msg: dict[str, Any]) -> Any:
        role = msg.get("role")
        if role == Role.USER.value:
            return ChatCompletionUserMessageParam(**msg)
        elif role == Role.SYSTEM.value:
            return ChatCompletionSystemMessageParam(**msg)
        elif role == Role.ASSISTANT.value:
            return ChatCompletionAssistantMessageParam(**msg)
        else:
            raise ValueError(f"Unknown role: {role}")

    def _retry_delay_seconds(self, error: RateLimitError, attempt: int) -> float:
        delay_seconds = min(0.5 * (2**attempt), 8.0)

        response = getattr(error, "response", None)
        headers = getattr(response, "headers", None)
        if headers:
            retry_after_ms = headers.get("retry-after-ms")
            if retry_after_ms is not None:
                try:
                    delay_seconds = max(delay_seconds, float(retry_after_ms) / 1000.0)
                except (TypeError, ValueError):
                    pass
            retry_after = headers.get("retry-after")
            if retry_after is not None:
                try:
                    delay_seconds = max(delay_seconds, float(retry_after))
                except (TypeError, ValueError):
                    pass

        message = str(error)
        match = re.search(r"try again in (\d+)\s*ms", message, flags=re.IGNORECASE)
        if match:
            delay_seconds = max(delay_seconds, float(match.group(1)) / 1000.0)

        return delay_seconds

    def generate(
        self, content: list[dict[str, Any]] | dict[str, Any] | str, **kwargs
    ) -> str | None:
        """Generates a response from the OpenAI API based on the provided content.
        Args:
            **kwargs:
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature for the generation.
        """

        if not self._client:
            raise ValueError("OpenAI client is not initialized.")

        if isinstance(content, str):
            content = [{"content": content, "role": Role.USER.value}]
        if isinstance(content, dict):
            content = [content]

        formatted_messages = [self._format_message(msg) for msg in content]
        max_retries = int(kwargs.get("max_retries", 6))

        for attempt in range(max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=kwargs.get("model") or self.model or GPTModel.best().value,
                    messages=formatted_messages,
                    max_tokens=kwargs.get("max_tokens")
                    or self._max_tokens
                    or MAX_TOKENS,
                    temperature=kwargs.get(
                        "temperature", TemperaturePresets.GENERAL.value
                    ),
                )
                return response.choices[0].message.content
            except RateLimitError as error:
                if attempt >= max_retries:
                    raise
                delay_seconds = self._retry_delay_seconds(error, attempt)
                LOGGER.warning(
                    "OpenAI rate limit reached, retrying",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    wait_seconds=round(delay_seconds, 3),
                )
                time.sleep(delay_seconds)

        return None
