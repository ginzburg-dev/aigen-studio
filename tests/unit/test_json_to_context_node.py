import pytest

from aigen.nodes.json_to_context import JsonToContextNode

pytestmark = pytest.mark.unit


def test_json_to_context_node_expands_dict_only():
    context = {
        "article_meta": {
            "page_name": "lost-landscapes",
            "page_title": "Lost Landscapes",
            "remaining_images_alt": ["alt1", "alt2"],
        }
    }
    node = JsonToContextNode(params={"input": "article_meta"})

    node.run(context)

    assert context["page_name"] == "lost-landscapes"
    assert context["page_title"] == "Lost Landscapes"
    assert context["remaining_images_alt"] == ["alt1", "alt2"]
    assert "remaining_images_alt_joined" not in context
    assert "article_meta_keys" not in context


def test_json_to_context_node_requires_dict_input():
    context = {"article_meta": "not-a-dict"}
    node = JsonToContextNode(params={"input": "article_meta"})

    with pytest.raises(ValueError):
        node.run(context)
