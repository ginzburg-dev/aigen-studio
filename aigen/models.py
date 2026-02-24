from enum import Enum
from typing import Any, Dict, List, Union, Generator, Iterable
from abc import ABC, abstractmethod


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class GPTModel(str, Enum):
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"

    @staticmethod
    def validate(model: str) -> bool:
        return model in [m.value for m in GPTModel]

    @classmethod
    def default(cls) -> "GPTModel":
        return cls.GPT_4O

    @staticmethod
    def get(model: str | None = None) -> str:
        if model and GPTModel.validate(model):
            return model
        return GPTModel.default().value


if __name__ == "__main__":
    # Example usage
    print("Available Roles:", [r.value for r in Role])
    print("Default Role:", Role.USER.value)

    print("Available GPT Models:", [m.value for m in GPTModel])
    print("Default GPT Model:", GPTModel.default().value)
    print("Get GPT Model (valid):", GPTModel.get("gpt-4-turbo"))
    print("Get GPT Model (invalid):", GPTModel.get("invalid-model"))
