from aigen.core.chat_session import ChatSession
from aigen.core.chat_history import ChatHistory
from aigen.core.prompt import Prompt
from aigen.gpt_prompt import GPTPrompt
from aigen.gpt_role import DEFAULT_GPT_ROLE, ROLE_GPT_ASSISTANT
from aigen.gpt_model import get_best_gpt_model, validate_gpt_model
import base64
from pathlib import Path
from openai import OpenAI
import yaml
from typing import Any, Optional, List, Dict

class GPTChatSession(ChatSession):
    def __init__(
            self, *,
            api_key: str,
            client: Optional[OpenAI] = None, 
            model: str = None, 
            max_tokens: int = 256,
            default_role=DEFAULT_GPT_ROLE,
            session_id: Optional[str] = None
    ) -> None:
        super().__init__(default_role=default_role, session_id=session_id)
        self.client = client or OpenAI(api_key=api_key)
        self.model = get_best_gpt_model(model)
        self.max_tokens = max_tokens

    def chat(
        self,
        extra_prompt: Optional[str] = None,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Any:
        # Optionally, you can add an extra prompt for this turn
        if extra_prompt:
            # Set extra_prompt to the session's temporal buffer
            self.add_text(extra_prompt)
        # Add constructed prompt buffer to history
        self._move_buffer_to_history()
        # Send all prompts (history) to model
        messages = self.history.data

        try:
            response = self.client.chat.completions.create(
                model=model if validate_gpt_model(model) else self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens
            )
        except Exception as e:
            print(f"Unexpected error: {e}")

        response_dict = response.model_dump() # Convert response object to dictionary
        assistant_message = response_dict["choices"][0]["message"]["content"]
        # Flush model's response to history
        self.history.add(GPTPrompt(role=ROLE_GPT_ASSISTANT, text=assistant_message))
        return assistant_message

    def _create_buffer(self) -> Any:
        return GPTPrompt()
