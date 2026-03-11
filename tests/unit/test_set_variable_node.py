import pytest

from aigen.nodes.set_variable import SetVariableNode

pytestmark = pytest.mark.unit


def test_set_variable_if_missing_true_keeps_existing_value():
    context = {"template_path": "from-csv.htm"}
    node = SetVariableNode(
        params={
            "name": "template_path",
            "value": "default-template.htm",
            "if_missing": True,
        }
    )

    node.run(context)

    assert context["template_path"] == "from-csv.htm"


def test_set_variable_if_missing_true_sets_when_missing():
    context: dict[str, str] = {}
    node = SetVariableNode(
        params={
            "name": "template_path",
            "value": "default-template.htm",
            "if_missing": True,
        }
    )

    node.run(context)

    assert context["template_path"] == "default-template.htm"
