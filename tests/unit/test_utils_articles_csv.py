import csv

import pytest

from aigen.common.article import read_article_contexts_from_csv

pytestmark = pytest.mark.unit


def test_read_article_contexts_from_csv(tmp_path):
    articles_root = tmp_path / "articles"
    article_dir = articles_root / "article-001"
    images_dir = article_dir / "images"
    images_dir.mkdir(parents=True)
    (article_dir / "startup_prompt.txt").write_text(
        "Use concise tone.", encoding="utf-8"
    )

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["article_path"])
        writer.writeheader()
        writer.writerow({"article_path": "articles/article-001"})

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-001"
    assert "images_path" not in contexts[0]
    assert contexts[0]["startup_prompt"] == "Use concise tone."


def test_read_article_contexts_from_csv_with_explicit_images_path(tmp_path):
    article_dir = tmp_path / "article-002"
    article_dir.mkdir(parents=True)
    custom_images = tmp_path / "shared-images"
    custom_images.mkdir(parents=True)

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["article_path", "images_path"])
        writer.writeheader()
        writer.writerow(
            {
                "article_path": "article-002",
                "images_path": "shared-images",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-002"
    assert contexts[0]["images_path"] == str(custom_images.resolve())


def test_read_article_contexts_from_csv_with_case_insensitive_columns(tmp_path):
    article_dir = tmp_path / "article-003"
    article_dir.mkdir(parents=True)
    custom_images = tmp_path / "imgs-003"
    custom_images.mkdir(parents=True)

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article_Path", "Images_Path"])
        writer.writeheader()
        writer.writerow(
            {
                "Article_Path": "article-003",
                "Images_Path": "imgs-003",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-003"
    assert contexts[0]["images_path"] == str(custom_images.resolve())


def test_read_article_contexts_from_csv_with_article_path_and_images_headers(tmp_path):
    article_dir = tmp_path / "article-004"
    article_dir.mkdir(parents=True)
    custom_images = tmp_path / "imgs-004"
    custom_images.mkdir(parents=True)

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article Path", "Images"])
        writer.writeheader()
        writer.writerow(
            {
                "Article Path": "article-004",
                "Images": "imgs-004",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-004"
    assert contexts[0]["images_path"] == str(custom_images.resolve())


def test_read_article_contexts_from_csv_with_instruction_column_and_base_dir(tmp_path):
    article_dir = tmp_path / "article-005"
    article_dir.mkdir(parents=True)

    instructions_dir = tmp_path / "instructions"
    instructions_dir.mkdir(parents=True)
    expected_instruction = instructions_dir / "rewrite.yaml"
    expected_instruction.write_text(
        "- node: SetVariable\n  params:\n    name: x\n    value: y\n", encoding="utf-8"
    )

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article Path", "Instruction"])
        writer.writeheader()
        writer.writerow(
            {
                "Article Path": "article-005",
                "Instruction": "rewrite",
            }
        )

    contexts = read_article_contexts_from_csv(
        str(csv_path), instructions_base_dir=str(instructions_dir)
    )
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-005"
    assert contexts[0]["instruction_path"] == str(expected_instruction.resolve())


def test_read_article_contexts_prefers_cwd_relative_path_if_exists(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    article_dir = tmp_path / "examples" / "articles" / "article-006"
    article_dir.mkdir(parents=True)
    csv_dir = tmp_path / "examples" / "articles"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "articles.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article Path"])
        writer.writeheader()
        writer.writerow({"Article Path": "examples/articles/article-006"})

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_path"] == str(article_dir.resolve())
    assert contexts[0]["article_name"] == "article-006"


def test_read_article_contexts_from_csv_with_template_path_column(tmp_path):
    article_dir = tmp_path / "article-007"
    article_dir.mkdir(parents=True)
    template_dir = tmp_path / "templates"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "artcabbage_article_template.htm"
    template_file.write_text("<html></html>\n", encoding="utf-8")

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Article Path", "Images", "Template Path"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "Article Path": "article-007",
                "Images": "",
                "Template Path": "templates/artcabbage_article_template.htm",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-007"
    assert contexts[0]["template_path"] == str(template_file.resolve())
