create-env-file:
	@cp .envs/template.env .env

install:
	uv sync --dev --all-extras

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

check-format:
	uv run ruff check --no-fix src tests

test:
	uv run pytest
