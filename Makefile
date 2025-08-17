.PHONY: run lint format

run:
	poetry run python -m src.main

lint:
	poetry run ruff check .

format:
	poetry run ruff format .