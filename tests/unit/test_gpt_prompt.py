import pytest

from aigen.prompt.openai import OpenAIPrompt

pytestmark = pytest.mark.unit


def test_gpt_prompt_init():
    prompt = OpenAIPrompt(text="test", role="user")
    print(prompt)
