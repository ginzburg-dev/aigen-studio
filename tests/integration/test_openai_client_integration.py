
import pytest

from aigen.client.openai import OpenAIClient
from aigen.models import GPTModel


@pytest.mark.integration
def test_openai_client_generate_smoke():
    client = OpenAIClient(model=GPTModel.GPT_4O_MINI.value, max_tokens=32)
    response = client.generate("Reply with one short word.")
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    print(response)
