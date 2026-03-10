import pytest

from aigen.nodes.copy_variable import CopyVariableNode

pytestmark = pytest.mark.unit


def test_copy_variable_node():
    context = {"var1": "Hello, World!"}
    params = {"input": "var1", "output": "var2"}
    copy_node = CopyVariableNode(params=params)
    copy_node.run(context)
    assert context["var2"] == "Hello, World!"
    print(context)
