# Test Layout

## Purpose

- `tests/unit`: fast, deterministic tests with mocks/stubs and no network calls.
- `tests/integration`: real dependency tests (external services, real infrastructure, API keys).

## Run Commands

- Unit (default): `PYTHONPATH=src .venv/bin/pytest`
- Unit only: `PYTHONPATH=src .venv/bin/pytest -m unit`
- Integration only: `PYTHONPATH=src .venv/bin/pytest -m integration`
- All tests: `PYTHONPATH=src .venv/bin/pytest -m "unit or integration"`
- Real integration execution: `RUN_INTEGRATION=1 OPENAI_API_KEY=... PYTHONPATH=src .venv/bin/pytest -m integration`

## Rules

- Put logic-only tests in `unit`.
- Put network/API tests in `integration`.
- Integration tests must be safe to skip when credentials are missing or opt-in is not enabled.
- Keep integration instruction fixtures under `tests/integration/instructions/`.
