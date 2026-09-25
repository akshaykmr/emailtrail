help:
	@echo "Usage:"
	@echo "    make help        show this message"
	@echo "    make setup       create virtual environment and install dependencies"
	@echo "    make test        run the tests"


setup:
	uv sync --locked

test:
	uv run --locked pytest
