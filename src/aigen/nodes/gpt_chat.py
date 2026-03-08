from aigen.common import prompt
from aigen.common.node import Node
from aigen.common.chat_session import ChatSession
from aigen.prompt.openai import OpenAIPrompt
from aigen.common.file_handler import FileHandler
from aigen.common.utils import replace_vars
from typing import Any, Dict, List, Optional, Union

class GPTChatNode(Node):
    def __init__(
            self,
            chat_session_id: str | None = None,
            model: str | None = None,
            max_tokens: int | None = None,
            temperature: float | None = None,
            use_cache: bool = False,
        ) -> None:
        super().__init__("GPTChat", **{'model': model, 'max_tokens': max_tokens, 'mode': mode, 'prompt': prompt})

    def run(self, context: dict[str, Any]) -> None:
        
        chat_history = self.params.get('chat_history', 'gptbuffer')
        chat_history = replace_vars(chat_history, context)
        if chat_history not in context:
                context[chat_history] = []
        output = self.params.get('output', "")
        output = replace_vars(output, context)
        if output == "":
            raise ValueError("Output is empty!")
        mode = self.params.get('mode', 'replace')
        max_tokens = self.params.get('max_tokens', 256)
        prompt = self.params.get('prompt', [])

        chat = GPTChatSession(api_key=api_key)
        chat.history.add(context[chat_history])

        for item in prompt:
            type = item.get('type')
            content = item.get('content')
            if type == "image":
                detailed: bool = item.get('detailed', True)
                if isinstance(content, str):
                    content = replace_vars(content, context)
                    image_path = context[content] if content in context else content
                    images = FileHandler.expand_images(image_path)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            i = replace_vars(i, context)
                            image_path = context[i] if i in context else i
                            images = FileHandler.expand_images(image_path)
                        else:
                            raise ValueError("Image files not found!")
                for i in images:
                    chat.add_image(i, detailed=detailed)
            if type == "text":
                if isinstance(content, str):
                    content = replace_vars(content, context)
                    text = context[content] if content in context else content
                    chat.add_text(text)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            i = replace_vars(i, context)
                            text = context[i] if i in context else i
                            chat.add_text(text)
                        else:
                            raise ValueError("Wrong content format!")
                else:
                    raise ValueError("Wrong content format!")

        response = chat.chat(max_tokens=max_tokens)
        
        context[chat_history] = chat.history.data

        if mode == 'append':
            if output not in context:
                context[output] = []
            context[output].append(response)
        else:
            context[output] = response

