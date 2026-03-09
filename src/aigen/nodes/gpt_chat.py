from pathlib import Path

from aigen.common import prompt
from aigen.common.node import Node
from aigen.common.chat_session import ChatSession
from aigen.prompt.openai import OpenAIPrompt
from aigen.client.openai import OpenAIClient
from aigen.common.file_handler import FileHandler
from aigen.common.utils import replace_vars
from typing import Any, Dict, List, Optional, Union

import structlog

LOGGER = structlog.get_logger(__name__)


class GPTChatNode(Node):
    def __init__(self, **params) -> None:
        super().__init__("GPTChat", **params)
        self._chat_sessions = ChatSession()

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)

        client = OpenAIClient()
        chat_history_key = params.get("input")
        model = params.get("model")
        model = params.get("temperature")
        max_tokens = params.get("max_tokens")
        prompt = params.get("prompt", [])
        output = params.get("output")
        if not output:
            raise ValueError("Output is empty.")
        
        if chat_history_key:
            if Path(chat_history_key).exists():
                self._chat_sessions.load_from_file(chat_history_key)
                LOGGER.info(
                    "Load GPTChat history from file",
                    filename=chat_history_key
                )
            else:
                if chat_history_key not in context:
                    context[chat_history_key] = []
                chat_history = context[chat_history_key]
                self._chat_sessions.set_history(chat_history)

        def _resolve_image_paths(image_path: str) -> list[str]:
            images = []
            if Path(image_path).is_dir():
                images = FileHandler.search_images(image_path)
            elif Path(image_path).is_file():
                images = [image_path]
            return images

        _prompt = OpenAIPrompt()
        for item in prompt:
            type = item.get("type")
            content = item.get("content")
            if type == "image":
                detailed: bool = item.get("detailed", True)
                images = []
                if isinstance(content, str):
                    image_path = context[content] if content in context else content
                    images = _resolve_image_paths(image_path)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            image_path = context[i] if i in context else i
                            images = _resolve_image_paths(image_path)
                        else:
                            raise ValueError("Wrong content format.")
                else:
                    raise ValueError("Wrong content format.")
                for i in images:
                    _prompt.add_image(i, detailed=detailed)

            if type == "text":
                if isinstance(content, str):
                    text = context[content] if content in context else content
                    _prompt.add_text(text)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            i = replace_vars(i, context)
                            text = context[i] if i in context else i
                            _prompt.add_text(text)
                        else:
                            raise ValueError("Wrong content format.")
                else:
                    raise ValueError("Wrong content format.")

        def _resolve_temperature(temperature: str | int):
            if isinstance
        response = client.generate(
            content=self._chat_sessions.history + _prompt.to_dict(),
            max_tokens=max_tokens,
            temperature=)
        
        context[chat_history] = chat.history.data

        if mode == 'append':
            if output not in context:
                context[output] = []
            context[output].append(response)
        else:
            context[output] = response

