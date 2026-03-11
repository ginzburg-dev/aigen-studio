import argparse
from datetime import datetime
from pathlib import Path
import re

import structlog

from aigen.article.csv_context import read_article_contexts_from_csv
from aigen.common.file_handler import FileHandler
from aigen.common.pipeline import process_actions
from aigen.config import AigenConfig

LOGGER = structlog.get_logger(__name__)
_VERSION_DIR_RE = re.compile(r"^v(\d+)$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate article outputs from instructions and article CSV."
    )
    parser.add_argument(
        "articles_csv",
        type=str,
        help="Path to CSV with article folder paths.",
    )
    parser.add_argument(
        "-i",
        "--instructions",
        type=str,
        default=None,
        help="Optional default instructions YAML. If omitted, each CSV row must provide Instructions.",
    )
    return parser


def reserve_generation_dir(article_path: str | Path) -> Path:
    article_dir = Path(article_path).expanduser().resolve()
    output_base = article_dir / "aigen"
    output_base.mkdir(parents=True, exist_ok=True)

    max_version = 0
    for child in output_base.iterdir():
        if not child.is_dir():
            continue
        match = _VERSION_DIR_RE.match(child.name)
        if not match:
            continue
        max_version = max(max_version, int(match.group(1)))

    next_version = max_version + 1
    while True:
        generation_dir = output_base / f"v{next_version:03d}"
        try:
            generation_dir.mkdir(parents=True, exist_ok=False)
            return generation_dir
        except FileExistsError:
            next_version += 1


def resolve_config_path(path_value: str, config_root_dir: Path | None) -> Path:
    candidate = Path(path_value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()

    if config_root_dir is not None:
        return (config_root_dir / candidate).resolve()

    return (Path.cwd() / candidate).resolve()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = AigenConfig()
    config_root_dir = config.get_config_root_dir()
    default_instructions_path: Path | None = None
    default_instructions: list[dict] | None = None
    if args.instructions:
        default_instructions_path = resolve_config_path(
            args.instructions, config_root_dir
        )
        default_instructions = FileHandler.read_yaml(str(default_instructions_path))

    article_contexts = read_article_contexts_from_csv(
        args.articles_csv,
        config_root_dir=str(config_root_dir) if config_root_dir else None,
    )

    if not article_contexts:
        LOGGER.warning("No article rows found in CSV", csv=args.articles_csv)
        return

    for index, context in enumerate(article_contexts, start=1):
        article_path = context.get("article_path")
        if not article_path:
            raise ValueError("Article context is missing 'article_path'.")

        generation_dir = reserve_generation_dir(str(article_path))
        context["generation_dir"] = str(generation_dir)
        context["generation_version"] = generation_dir.name

        now = datetime.now()
        current_year = str(now.year)
        current_date = now.date().isoformat()
        current_date_human = f"{now.strftime('%B')} {now.day}, {now.year}"
        context.setdefault("current_year", current_year)
        context.setdefault("current_date", current_date)
        context.setdefault("current_date_human", current_date_human)
        context.setdefault("copyright_year", f"© {current_year}")

        instruction_path = context.get("instruction_path")
        if instruction_path:
            instructions = FileHandler.read_yaml(str(instruction_path))
            resolved_instruction_path = str(instruction_path)
        elif default_instructions is not None:
            instructions = default_instructions
            resolved_instruction_path = (
                str(default_instructions_path) if default_instructions_path else ""
            )
        else:
            raise ValueError(
                "No instructions provided. Pass --instructions or set Instructions in CSV row."
            )
        LOGGER.info(
            "Processing article",
            index=index,
            total=len(article_contexts),
            article_path=context.get("article_path"),
            generation_dir=context.get("generation_dir"),
            images_path=context.get("images_path"),
            template_path=context.get("template_path"),
            instruction_path=resolved_instruction_path,
            has_startup_prompt="startup_prompt" in context,
        )
        process_actions(context, instructions)


if __name__ == "__main__":
    main()
