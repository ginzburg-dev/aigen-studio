import csv

import pytest

from aigen.article.csv_context import read_article_contexts_from_csv

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


def test_read_article_contexts_from_csv_with_instruction_column_and_config_root(
    tmp_path,
):
    article_dir = tmp_path / "article-005"
    article_dir.mkdir(parents=True)

    config_root = tmp_path / "config"
    config_root.mkdir(parents=True)
    expected_instruction = config_root / "rewrite.yaml"
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
        str(csv_path), config_root_dir=str(config_root)
    )
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-005"
    assert contexts[0]["instruction_path"] == str(expected_instruction.resolve())


def test_read_article_contexts_from_csv_with_instructions_column_path(tmp_path):
    article_dir = tmp_path / "article-005b"
    article_dir.mkdir(parents=True)

    pipeline_dir = tmp_path / "custom_pipeline"
    pipeline_dir.mkdir(parents=True)
    instruction_file = pipeline_dir / "artcabbage_article_html_pipeline.yaml"
    instruction_file.write_text(
        "- node: SetVariable\n  params:\n    name: x\n    value: y\n", encoding="utf-8"
    )

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article Path", "Instructions"])
        writer.writeheader()
        writer.writerow(
                {
                    "Article Path": "article-005b",
                    "Instructions": "custom_pipeline/artcabbage_article_html_pipeline.yaml",
                }
            )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-005b"
    assert contexts[0]["instruction_path"] == str(instruction_file.resolve())


def test_read_article_contexts_from_csv_resolves_template_from_config_root(tmp_path):
    article_dir = tmp_path / "article-005c"
    article_dir.mkdir(parents=True)

    config_root = tmp_path / "config"
    template_dir = config_root / "templates"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "artcabbage_article_template.htm"
    template_file.write_text("<html>template</html>\n", encoding="utf-8")

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article", "HTML Template"])
        writer.writeheader()
        writer.writerow(
            {
                "Article": "article-005c",
                "HTML Template": "templates/artcabbage_article_template.htm",
            }
        )

    contexts = read_article_contexts_from_csv(
        str(csv_path), config_root_dir=str(config_root)
    )
    assert len(contexts) == 1
    assert contexts[0]["template_path"] == str(template_file.resolve())


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


def test_read_article_contexts_from_csv_with_template_column(tmp_path):
    article_dir = tmp_path / "article-008"
    article_dir.mkdir(parents=True)
    template_dir = tmp_path / "templates"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "row_template.htm"
    template_file.write_text("<html>row template</html>\n", encoding="utf-8")

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article", "Images", "Template"])
        writer.writeheader()
        writer.writerow(
            {
                "Article": "article-008",
                "Images": "",
                "Template": "templates/row_template.htm",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-008"
    assert contexts[0]["template_path"] == str(template_file.resolve())


def test_read_article_contexts_from_csv_with_html_template_column(tmp_path):
    article_dir = tmp_path / "article-008b"
    article_dir.mkdir(parents=True)
    template_dir = tmp_path / "templates"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "row_template_html.htm"
    template_file.write_text("<html>row html template</html>\n", encoding="utf-8")

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article", "Images", "HTML Template"])
        writer.writeheader()
        writer.writerow(
            {
                "Article": "article-008b",
                "Images": "",
                "HTML Template": "templates/row_template_html.htm",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-008b"
    assert contexts[0]["template_path"] == str(template_file.resolve())


def test_read_article_contexts_from_csv_with_section_author_and_cover(tmp_path):
    article_dir = tmp_path / "article-009"
    article_dir.mkdir(parents=True)

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Article Path",
                "Section",
                "Article Section",
                "Author Name",
                "Author Type",
                "Cover Image URL",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Article Path": "article-009",
                "Section": "Visual Arts/",
                "Article Section": "Visual Art",
                "Author Name": "Wilson Burge",
                "Author Type": "organization",
                "Cover Image URL": "https://www.artcabbage.com/images/visual/cover.png",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-009"
    assert contexts[0]["section"] == "visual-arts"
    assert contexts[0]["article_section"] == "Visual Art"
    assert contexts[0]["author_name"] == "Wilson Burge"
    assert contexts[0]["author_type"] == "Organization"
    assert (
        contexts[0]["cover_image_url"]
        == "https://www.artcabbage.com/images/visual/cover.png"
    )


def test_read_article_contexts_from_csv_with_prompt_step_1(tmp_path):
    article_dir = tmp_path / "article-010"
    article_dir.mkdir(parents=True)

    csv_path = tmp_path / "articles.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Article", "Prompt Step 1"])
        writer.writeheader()
        writer.writerow(
            {
                "Article": "article-010",
                "Prompt Step 1": "Describe these works in exactly three sentences.",
            }
        )

    contexts = read_article_contexts_from_csv(str(csv_path))
    assert len(contexts) == 1
    assert contexts[0]["article_name"] == "article-010"
    assert (
        contexts[0]["prompt_step_1"]
        == "Describe these works in exactly three sentences."
    )
