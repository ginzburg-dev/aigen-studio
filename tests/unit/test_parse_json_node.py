import pytest

from aigen.nodes.parse_json import ParseJSONNode

pytestmark = pytest.mark.unit


def test_parse_json_node_sets_context_variables():
    context = {
        "article_meta_json": (
            '{"page_name":"lost-landscapes","cover_image_alt":"cover alt",'
            '"remaining_images_alt":["alt1","alt2"],"page_title":"Lost Landscapes",'
            '"description":"Description text"}'
        )
    }
    node = ParseJSONNode(
        params={
            "input": "article_meta_json",
            "output": "article_meta",
        }
    )

    node.run(context)

    assert context["article_meta"]["page_name"] == "lost-landscapes" # type: ignore
    assert context["article_meta"]["remaining_images_alt"] == ["alt1", "alt2"] # type: ignore
    assert "page_title" not in context
    assert "description" not in context
    assert "remaining_images_alt_joined" not in context
    assert "article_meta_json_keys" not in context


def test_parse_json_node_raises_on_non_object():
    context = {"article_meta_json": '["x", "y"]'}
    node = ParseJSONNode(params={"input": "article_meta_json"})

    with pytest.raises(ValueError):
        node.run(context)


def test_parse_json_node_defaults_output_name():
    context = {"article_meta_json": '{"x": 1, "y": 2}'}
    node = ParseJSONNode(params={"input": "article_meta_json"})

    node.run(context)

    assert context["article_meta_json_obj"] == {"x": 1, "y": 2}
