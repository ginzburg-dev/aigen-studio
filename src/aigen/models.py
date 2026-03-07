from enum import Enum
from http import client
from os import path
from openai import OpenAI
from pydantic import B

from typing import Any


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class GPTModel(str, Enum):
    # Latest & fastest
    GPT_5_2 = "gpt-5.2"
    GPT_5_1 = "gpt-5.1"
    GPT_5 = "gpt-5"
    
    # Current flagship
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    
    # Previous flagship
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    
    # Earlier versions
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Reasoning models
    O1 = "o1"
    O1_MINI = "o1-mini"
    O3_MINI = "o3-mini"
    
    # Specialized
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    WHISPER_1 = "whisper-1"
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"

    @staticmethod
    def validate(model: str) -> bool:
        return model in [m.value for m in GPTModel]

    @classmethod
    def best(cls) -> GPTModel:
        return cls(GPTModel.GPT_5_2)

    @staticmethod
    def get(model: str) -> GPTModel:
        if model and GPTModel.validate(model):
            return GPTModel(model)
        return GPTModel.best()


class ImageType(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    GIF = "gif"
    BMP = "bmp"
    WEBP = "webp"

    @staticmethod
    def validate(ext: str) -> bool:
        return ext in [i.value for i in ImageType]


class TemperaturePresets(float, Enum):
    ANALYSIS = 0.3
    CREATIVITY = 0.85
    GENERAL = 0.7
