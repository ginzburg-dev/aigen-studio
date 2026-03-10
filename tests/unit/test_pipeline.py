import pytest
from typing import Any

from aigen.common.file_handler import FileHandler
from aigen.common.pipeline import process_actions

pytestmark = pytest.mark.unit


def test_gpt_model_validation():
    instructions = FileHandler.read_yaml("pipeline/test_pipeline.yaml")
    context: dict[str, Any] = {}
    process_actions(context, instructions)
