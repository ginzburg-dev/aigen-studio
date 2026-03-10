import pytest

from aigen.common.node_registry import NODE_REGISTRY

pytestmark = pytest.mark.unit


def test_node_registry():
    assert "CopyVariable" in NODE_REGISTRY
    assert "GPTChat" in NODE_REGISTRY
    assert "PrintVariable" in NODE_REGISTRY
    assert "ReadFile" in NODE_REGISTRY
    assert "ReplaceBetween" in NODE_REGISTRY
    assert "SetVariable" in NODE_REGISTRY
    assert "WriteFile" in NODE_REGISTRY
    print(NODE_REGISTRY)
