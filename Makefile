.PHONY: install test lint format run docker-up

install:
	python -m pip install -e ".[dev]"

test:
	pytest --cov=quantumshield --cov-report=term-missing

lint:
	ruff check .
	mypy src

format:
	ruff format .

run:
	uvicorn quantumshield.api.main:app --reload

docker-up:
	docker compose up --build
