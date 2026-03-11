from pathlib import Path
from typing import Any

from aigen.client.openai import OpenAIClient
from aigen.common.chat_session import ChatSession
from aigen.common.file_handler import FileHandler
from aigen.common.node import Node
from aigen.common.node_registry import register_node
from aigen.constants import MAX_TOKENS
from aigen.models import GPTModel, Role
from aigen.prompt.openai import OpenAIPrompt

import structlog

LOGGER = structlog.get_logger(__name__)


@register_node("GPTChat")
class GPTChatNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        self._chat_session = ChatSession()

    def _load_history(self, chat_history_key: str, context: dict[str, Any]) -> bool:
        if Path(chat_history_key).is_file():
            self._chat_session.load_from_file(chat_history_key)
            LOGGER.info(
                "Loaded GPT chat history from file",
                history_key=chat_history_key,
                history_size=len(self._chat_session.history),
            )
            return True

        history = context.get(chat_history_key, [])
        if not isinstance(history, list):
            raise ValueError(f"History '{chat_history_key}' must be a list.")
        self._chat_session.set_history(history)
        LOGGER.info(
            "Loaded GPT chat history from context variable",
            history_key=chat_history_key,
            history_size=len(self._chat_session.history),
        )
        return False

    def _resolve_image_paths(self, image_path: str) -> list[str]:
        path = Path(image_path)
        if path.is_dir():
            return FileHandler.search_images(image_path)
        if path.is_file():
            return [image_path]
        return []

    def _build_user_message(
        self,
        prompt_items: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = OpenAIPrompt(role=Role.USER.value)
        for item in prompt_items:
            item_type = item.get("type")
            content = item.get("content")
            if item_type == "image":
                detailed = bool(item.get("detailed", True))
                resolved_content = (
                    context.get(content, content)
                    if isinstance(content, str)
                    else content
                )
                values = (
                    resolved_content
                    if isinstance(resolved_content, list)
                    else [resolved_content]
                )
                for value in values:
                    if not value:
                        continue
                    if not isinstance(value, str):
                        raise ValueError("Wrong content format.")
                    image_path = str(context.get(value, value))
                    for resolved_path in self._resolve_image_paths(image_path):
                        prompt.add_image(resolved_path, detailed=detailed)
            elif item_type == "text":
                values = content if isinstance(content, list) else [content]
                for value in values:
                    if not isinstance(value, str):
                        raise ValueError("Wrong content format.")
                    prompt.add_text(str(context.get(value, value)))
            else:
                raise ValueError(f"Unsupported prompt item type: {item_type}")

        return {"role": Role.USER.value, "content": prompt.to_dict()}

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)

        output = params.get("output")
        if not output:
            raise ValueError("Output is empty.")

        chat_history_key = params.get("chat_history") or params.get("input")
        history_from_file = False
        if chat_history_key:
            history_from_file = self._load_history(str(chat_history_key), context)

        prompt_items = params.get("prompt", [])
        if not isinstance(prompt_items, list):
            raise ValueError("Prompt must be a list.")
        user_message = self._build_user_message(prompt_items, context)
        self._chat_session.add_dict(user_message)

        model = params.get("model") or GPTModel.best().value
        max_tokens = int(params.get("max_tokens", MAX_TOKENS))
        client = OpenAIClient(model=model, max_tokens=max_tokens)

        response = client.generate(
            content=self._chat_session.history,
            model=model,
            max_tokens=max_tokens,
            temperature=params.get("temperature"),
        )
        if response is None:
            raise ValueError("Model returned empty response.")

        LOGGER.info("GPTChat response received", response_chars=len(str(response)), response=str(response))

        self._chat_session.add_dict(
            {"role": Role.ASSISTANT.value, "content": str(response)}
        )
        context[str(output)] = str(response)

        if chat_history_key:
            chat_history_key = str(chat_history_key)
            if history_from_file:
                self._chat_session.save_to_file(chat_history_key)
                LOGGER.info(
                    "Saved GPT chat history to file",
                    history_key=chat_history_key,
                    history_size=len(self._chat_session.history),
                )
            else:
                context[chat_history_key] = list(self._chat_session.history)
                LOGGER.info(
                    "Saved GPT chat history to context variable",
                    history_key=chat_history_key,
                    history_size=len(self._chat_session.history),
                )
