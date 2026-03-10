import pytest

from aigen.nodes.replace_between import ReplaceBetweenNode

pytestmark = pytest.mark.unit


def test_replace_between_node():
    context = {
        "template": "before\n<!--Paste from here-->\nold\n<!--Paste to here-->\nafter",
        "replacement_block": "<p>new content</p>",
    }
    node = ReplaceBetweenNode(
        params={
            "input": "template",
            "output": "rendered",
            "start_marker": "<!--Paste from here-->",
            "end_marker": "<!--Paste to here-->",
            "replacement": "replacement_block",
        }
    )

    node.run(context)

    assert "rendered" in context
    assert "<p>new content</p>" in context["rendered"]
    assert "old" not in context["rendered"]


def test_replace_between_node_preserves_marker_indent():
    context = {
        "template": (
            "before\n"
            "                 <!--Paste from here-->\n"
            "                 old\n"
            "                 <!--Paste to here-->\n"
            "after"
        ),
        "replacement_block": "<h1>Title</h1>\n<p>Body</p>",
    }
    node = ReplaceBetweenNode(
        params={
            "input": "template",
            "output": "rendered",
            "start_marker": "<!--Paste from here-->",
            "end_marker": "<!--Paste to here-->",
            "replacement": "replacement_block",
        }
    )

    node.run(context)

    assert "\n                 <h1>Title</h1>\n" in context["rendered"]
    assert "\n                 <p>Body</p>\n" in context["rendered"]


def test_replace_between_node_errors_on_missing_markers():
    context = {"template": "no markers here", "replacement_block": "x"}
    node = ReplaceBetweenNode(
        params={
            "input": "template",
            "output": "rendered",
            "start_marker": "<!--Paste from here-->",
            "end_marker": "<!--Paste to here-->",
            "replacement": "replacement_block",
        }
    )

    with pytest.raises(ValueError):
        node.run(context)
