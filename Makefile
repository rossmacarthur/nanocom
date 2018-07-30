.PHONY: help clean build build-all lint run

help:
	@echo "clean      Remove all build artifacts."
	@echo "build      Create venv and install package."
	@echo "build-all  Create venv and install package and development dependencies."
	@echo "lint       Run PEP8 lints."
	@echo "help       Show this message and exit."

clean:
	find . -name \*.pyc -o -name \*.pyo -o -name __pycache__ -delete
	rm -rf build dist wheels venv *.egg-info

build:
	virtualenv --python=python3 venv
	venv/bin/pip install -e .

build-all:
	virtualenv --python=python3 venv
	venv/bin/pip install -e .[linting]

lint:
	venv/bin/flake8 .
