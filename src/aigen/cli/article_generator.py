import argparse

import structlog

from aigen.common.article import read_article_contexts_from_csv
from aigen.common.file_handler import FileHandler
from aigen.common.pipeline import process_actions
from aigen.config import AigenConfig

LOGGER = structlog.get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate article outputs from instructions and article CSV."
    )
    parser.add_argument("instructions", type=str, help="Path to instructions YAML.")
    parser.add_argument(
        "articles_csv",
        type=str,
        help="Path to CSV with article folder paths.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = AigenConfig()
    default_instructions = FileHandler.read_yaml(args.instructions)
    instructions_dir = config.get_instructions_dir()
    article_contexts = read_article_contexts_from_csv(
        args.articles_csv,
        instructions_base_dir=str(instructions_dir) if instructions_dir else None,
    )

    if not article_contexts:
        LOGGER.warning("No article rows found in CSV", csv=args.articles_csv)
        return

    for index, context in enumerate(article_contexts, start=1):
        instruction_path = context.get("instruction_path")
        instructions = (
            FileHandler.read_yaml(instruction_path)
            if instruction_path
            else default_instructions
        )
        LOGGER.info(
            "Processing article",
            index=index,
            total=len(article_contexts),
            article_path=context.get("article_path"),
            images_path=context.get("images_path"),
            template_path=context.get("template_path"),
            instruction_path=instruction_path or args.instructions,
            has_startup_prompt="startup_prompt" in context,
        )
        process_actions(context, instructions)


if __name__ == "__main__":
    main()
