.PHONY: create-env-file install format check-format unit-test integration-test test

create-env-file:
	@cp .envs/template.env .env

install:
	uv sync --dev --all-extras

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

quality-check:
	uv run ruff check --no-fix src tests

unit-test:
	PYTHONPATH=src uv run pytest -s tests/unit

integration-test:
	dotenv run env PYTHONPATH=src uv run pytest -s -m integration tests/integration

test: unit-test integration-test
