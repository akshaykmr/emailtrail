.PHONY: help setup test lint format build

help:
	@echo "make setup   install the project and development tools with uv"
	@echo "make test    run tests"
	@echo "make lint    check lint and formatting"
	@echo "make format  format Python files"
	@echo "make build   build and validate release distributions"

setup:
	uv sync --locked

test:
	uv run --locked pytest

lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .

format:
	uv run --locked ruff format .

build:
	uv build
	uv run --locked twine check --strict dist/*.whl dist/*.tar.gz
