import csv
from pathlib import Path
from typing import Any


def read_article_contexts_from_csv(
    csv_path: str, *, config_root_dir: str | None = None
) -> list[dict[str, Any]]:
    """Build per-article contexts from CSV rows.

    Expected CSV: either a named path column (`article_path`, `path`, `article`)
    or a single unnamed first column containing article folder paths.
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    config_root = (
        Path(config_root_dir).expanduser().resolve() if config_root_dir else None
    )

    path_keys = ("article_path", "path", "article")
    images_keys = ("images_path", "images_dir", "images_folder", "images")
    template_keys = ("template_path", "template", "html_template", "template_file")
    instruction_keys = ("instruction", "instructions", "instruction_name")
    section_keys = ("section", "section_slug", "category_slug")
    article_section_keys = ("article_section", "section_name", "section_title")
    author_keys = ("author_name", "author", "byline")
    author_type_keys = ("author_type", "author_kind", "author_schema_type")
    cover_image_url_keys = (
        "cover_image_url",
        "cover_url",
        "cover_image",
        "cover_image_path",
        "cover",
    )
    prompt_step_1_keys = ("prompt_step_1", "first_prompt", "prompt1")
    startup_prompt_files = (
        "startup_prompt.txt",
        "startup_prompt.md",
    )

    def first_non_empty_value(
        normalized_row: dict[str, Any], keys: tuple[str, ...]
    ) -> str | None:
        for key in keys:
            value = normalized_row.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        return None

    contexts: list[dict[str, Any]] = []
    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized: dict[str, Any] = {}
            for k, v in row.items():
                if k is None:
                    continue
                key = str(k).strip().lower().replace("-", "_").replace(" ", "_")
                normalized[key] = v

            article_path_value = first_non_empty_value(normalized, path_keys)

            if not article_path_value:
                values = [str(v).strip() for v in row.values() if v]
                if values:
                    article_path_value = values[0]

            if not article_path_value:
                continue

            article_dir = Path(article_path_value).expanduser()
            if not article_dir.is_absolute():
                by_cwd = (Path.cwd() / article_dir).resolve()
                by_csv = (csv_file.parent / article_dir).resolve()
                if by_cwd.exists():
                    article_dir = by_cwd
                elif by_csv.exists():
                    article_dir = by_csv
                else:
                    # Default new/uncreated article paths to CWD, not CSV dir.
                    article_dir = by_cwd
            else:
                article_dir = article_dir.resolve()

            context: dict[str, Any] = {
                "article_path": str(article_dir),
                "article_name": article_dir.name,
            }

            images_path_value = first_non_empty_value(normalized, images_keys)

            if images_path_value:
                candidate = Path(images_path_value)
                if not candidate.is_absolute():
                    by_cwd = (Path.cwd() / candidate).resolve()
                    by_article = (article_dir / candidate).resolve()
                    by_csv = (csv_file.parent / candidate).resolve()
                    if by_cwd.exists():
                        candidate = by_cwd
                    elif by_article.exists():
                        candidate = by_article
                    else:
                        candidate = by_csv
                if candidate.exists():
                    context["images_path"] = str(candidate)

            template_path_value = first_non_empty_value(normalized, template_keys)

            if template_path_value:
                candidate = Path(template_path_value).expanduser()
                if candidate.is_absolute():
                    candidate = candidate.resolve()
                elif config_root is not None:
                    candidate = (config_root / candidate).resolve()
                else:
                    by_cwd = (Path.cwd() / candidate).resolve()
                    by_article = (article_dir / candidate).resolve()
                    by_csv = (csv_file.parent / candidate).resolve()
                    if by_cwd.exists():
                        candidate = by_cwd
                    elif by_article.exists():
                        candidate = by_article
                    else:
                        candidate = by_csv
                context["template_path"] = str(candidate)

            instruction_value = first_non_empty_value(normalized, instruction_keys)

            if instruction_value:
                candidate = Path(instruction_value)
                if candidate.suffix == "":
                    candidate = candidate.with_suffix(".yaml")

                if candidate.is_absolute():
                    candidate = candidate.resolve()
                elif config_root is not None:
                    candidate = (config_root / candidate).resolve()
                else:
                    by_cwd = (Path.cwd() / candidate).resolve()
                    by_article = (article_dir / candidate).resolve()
                    by_csv = (csv_file.parent / candidate).resolve()

                    if by_cwd.exists():
                        candidate = by_cwd
                    elif by_article.exists():
                        candidate = by_article
                    elif by_csv.exists():
                        candidate = by_csv
                    else:
                        candidate = by_csv

                context["instruction_path"] = str(candidate)

            section_value = first_non_empty_value(normalized, section_keys)
            if section_value:
                context["section"] = section_value.strip("/").lower().replace(" ", "-")

            article_section_value = first_non_empty_value(
                normalized, article_section_keys
            )
            if article_section_value:
                context["article_section"] = article_section_value

            author_value = first_non_empty_value(normalized, author_keys)
            if author_value:
                context["author_name"] = author_value

            author_type_value = first_non_empty_value(normalized, author_type_keys)
            if author_type_value:
                lowered = author_type_value.strip().lower()
                if lowered == "person":
                    context["author_type"] = "Person"
                elif lowered in {"organization", "organisation"}:
                    context["author_type"] = "Organization"
                else:
                    context["author_type"] = author_type_value.strip()

            cover_image_url_value = first_non_empty_value(
                normalized, cover_image_url_keys
            )
            if cover_image_url_value:
                context["cover_image_url"] = cover_image_url_value

            prompt_step_1_value = first_non_empty_value(normalized, prompt_step_1_keys)
            if prompt_step_1_value:
                context["prompt_step_1"] = prompt_step_1_value

            for filename in startup_prompt_files:
                startup_prompt = article_dir / filename
                if startup_prompt.exists():
                    context["startup_prompt"] = startup_prompt.read_text(
                        encoding="utf-8"
                    ).strip()
                    break

            contexts.append(context)

    return contexts
