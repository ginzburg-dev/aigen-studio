import csv
from pathlib import Path
from typing import Any


def read_article_contexts_from_csv(
    csv_path: str, *, instructions_base_dir: str | None = None
) -> list[dict[str, Any]]:
    """Build per-article contexts from CSV rows.

    Expected CSV: either a named path column (`article_path`, `path`, `article`)
    or a single unnamed first column containing article folder paths.
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    path_keys = ("article_path", "path", "article")
    images_keys = ("images_path", "images_dir", "images_folder", "images")
    template_keys = ("template_path", "template", "html_template", "template_file")
    instruction_keys = ("instruction", "instructions", "instruction_name")
    startup_prompt_files = (
        "startup_prompt.txt",
        "startup_prompt.md",
    )

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

            article_path_value = None
            for key in path_keys:
                value = normalized.get(key.lower())
                if value:
                    article_path_value = value.strip()
                    break

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
                article_dir = by_cwd if by_cwd.exists() else by_csv
            else:
                article_dir = article_dir.resolve()

            context: dict[str, Any] = {
                "article_path": str(article_dir),
                "article_name": article_dir.name,
            }

            images_path_value = None
            for key in images_keys:
                value = normalized.get(key.lower())
                if value:
                    images_path_value = value.strip()
                    break

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

            template_path_value = None
            for key in template_keys:
                value = normalized.get(key.lower())
                if value:
                    template_path_value = value.strip()
                    break

            if template_path_value:
                candidate = Path(template_path_value).expanduser()
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
                else:
                    candidate = candidate.resolve()
                context["template_path"] = str(candidate)

            instruction_value = None
            for key in instruction_keys:
                value = normalized.get(key.lower())
                if value:
                    instruction_value = value.strip()
                    break

            if instruction_value:
                instruction_path = Path(instruction_value)
                if instruction_path.suffix == "":
                    instruction_path = instruction_path.with_suffix(".yaml")
                if not instruction_path.is_absolute():
                    if instructions_base_dir:
                        instruction_path = (
                            Path(instructions_base_dir) / instruction_path
                        ).resolve()
                    else:
                        instruction_path = (
                            csv_file.parent / instruction_path
                        ).resolve()
                context["instruction_path"] = str(instruction_path)

            for filename in startup_prompt_files:
                startup_prompt = article_dir / filename
                if startup_prompt.exists():
                    context["startup_prompt"] = startup_prompt.read_text(
                        encoding="utf-8"
                    ).strip()
                    break

            contexts.append(context)

    return contexts
