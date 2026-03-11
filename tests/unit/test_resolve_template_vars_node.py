import pytest

from aigen.nodes.resolve_template_vars import ResolveTemplateVars

pytestmark = pytest.mark.unit


def test_resolve_template_vars_node_replaces_variables():
    context = {
        "template_html": "<title>${page_title}</title><meta name='description' content='${description}'>",
        "page_title": "Lost Landscapes",
        "description": "Article description",
    }
    node = ResolveTemplateVars(
        params={
            "input": "template_html",
            "output": "rendered_html",
            "strict": True,
        }
    )

    node.run(context)

    assert context["rendered_html"] == (
        "<title>Lost Landscapes</title>"
        "<meta name='description' content='Article description'>"
    )


def test_resolve_template_vars_node_strict_mode_fails_on_unresolved_vars():
    context = {"template_html": "<title>${page_title}</title>"}
    node = ResolveTemplateVars(
        params={"input": "template_html", "output": "rendered_html", "strict": True}
    )

    with pytest.raises(ValueError):
        node.run(context)


def test_resolve_template_vars_node_serializes_list_as_json():
    context = {
        "template_html": '{"keywords": ${keywords}}',
        "keywords": ["ArtCabbage", "Visual Art", "Rita Louis"],
    }
    node = ResolveTemplateVars(
        params={
            "input": "template_html",
            "output": "rendered_html",
            "strict": True,
        }
    )

    node.run(context)

    assert (
        context["rendered_html"]
        == '{"keywords": ["ArtCabbage", "Visual Art", "Rita Louis"]}'
    )
