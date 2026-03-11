import pytest

from aigen.cli.article_generator import build_parser, reserve_generation_dir

pytestmark = pytest.mark.unit


def test_reserve_generation_dir_starts_with_v001(tmp_path):
    article_dir = tmp_path / "article-alpha"
    article_dir.mkdir(parents=True)

    generation_dir = reserve_generation_dir(article_dir)

    assert generation_dir == article_dir / "aigen" / "v001"
    assert generation_dir.exists()
    assert generation_dir.is_dir()


def test_reserve_generation_dir_increments_existing_versions(tmp_path):
    article_dir = tmp_path / "article-beta"
    base = article_dir / "aigen"
    (base / "v001").mkdir(parents=True)
    (base / "v002").mkdir(parents=True)
    (base / "notes").mkdir(parents=True)
    (base / "vXYZ").mkdir(parents=True)

    generation_dir = reserve_generation_dir(article_dir)

    assert generation_dir == article_dir / "aigen" / "v003"
    assert generation_dir.exists()


def test_build_parser_accepts_articles_csv_without_default_instructions():
    parser = build_parser()
    args = parser.parse_args(["examples/articles/articles.csv"])

    assert args.articles_csv == "examples/articles/articles.csv"
    assert args.instructions is None


def test_build_parser_accepts_optional_default_instructions_flag():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--instructions",
            "pipeline/artcabbage_article_html_pipeline.yaml",
            "examples/articles/articles.csv",
        ]
    )

    assert args.instructions == "pipeline/artcabbage_article_html_pipeline.yaml"
    assert args.articles_csv == "examples/articles/articles.csv"
