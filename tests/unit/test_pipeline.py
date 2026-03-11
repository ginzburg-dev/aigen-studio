import pytest
from typing import Any

from aigen.common.pipeline import process_actions

pytestmark = pytest.mark.unit


def test_gpt_model_validation():
    instructions = [
        {
            "node": "SetVariable",
            "params": {"name": "source_text", "value": "hello from test pipeline"},
        },
        {
            "node": "CopyVariable",
            "params": {"input": "source_text", "output": "copied_text"},
        },
    ]
    context: dict[str, Any] = {}
    process_actions(context, instructions)
    assert context["copied_text"] == "hello from test pipeline"
