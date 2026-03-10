from pathlib import Path

import pytest

from aigen.common.file_handler import FileHandler
from aigen.common.pipeline import process_actions


@pytest.mark.integration
def test_gpt_pipeline_instructions():
    instructions = FileHandler.read_yaml(
        "tests/integration/instructions/gpt_test_instructions.yaml"
    )
    context: dict = {}
    process_actions(context, instructions)

    assert "gpt_response_from_var" in context
    assert isinstance(context["gpt_response_from_var"], str)
    assert len(context["gpt_response_from_var"].strip()) > 0

    assert "gpt_history" in context
    assert isinstance(context["gpt_history"], list)
    assert len(context["gpt_history"]) >= 2

    assert "gpt_response_from_file" in context
    assert isinstance(context["gpt_response_from_file"], str)
    assert len(context["gpt_response_from_file"].strip()) > 0

    assert "history_file_content" in context
    assert isinstance(context["history_file_content"], str)
    assert "role" in context["history_file_content"]

    history_file = Path(context["history_file"])
    assert history_file.exists()
    response_file = Path(context["response_file"])
    assert response_file.exists()

    assert "first_response_from_file" in context
    assert context["first_response_from_file"] == context["gpt_response_from_file"]

    assert "gpt_response_modified" in context
    assert isinstance(context["gpt_response_modified"], str)
    assert len(context["gpt_response_modified"].strip()) > 0

    print("\n\n gpt_response_from_var:", context["gpt_response_from_var"])
    print("gpt_response_from_file:", context["gpt_response_from_file"])
    print("gpt_response_modified:", context["gpt_response_modified"])
    print("history_file:", history_file)
    print("response_file:", response_file)
