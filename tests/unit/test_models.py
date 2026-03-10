import pytest

from aigen.models import GPTModel

pytestmark = pytest.mark.unit


def test_gpt_model_validation():
    assert GPTModel.validate("gpt-4o")
    assert GPTModel.validate("gpt-4-turbo")
    assert GPTModel.validate("gpt-3.5-turbo")
    assert not GPTModel.validate("invalid-model")
