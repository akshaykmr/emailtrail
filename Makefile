help:
	@echo "Usage:"
	@echo "    make help        show this message"
	@echo "    make setup       create virtual environment and install dependencies"
	@echo "    make activate    enter virtual environment"
	@echo "    make test        run the tests"


setup:
	pip install pipenv
	pipenv install --dev

activate:
	pipenv shell

test:
	pipenv run pytest
