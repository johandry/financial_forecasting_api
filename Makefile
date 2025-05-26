.PHONY: run install test clean seed dc-run dc-test dc-seed lint

# Install all dependencies
install:
	poetry install

# Run the FastAPI app (dev mode)
run:
	ENV=local poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	POSTGRES_DB=forecast_test_db docker compose up -d redis db
	ENV=test poetry run pytest

# Seed the database with test data
seed:
	docker compose up -d db
	ENV=local PYTHONPATH=. poetry run python app/core/seed.py

#  Lint and auto-fix the code using black and isort, then check with flake8
fmt:
	poetry run black app tests
	poetry run isort app tests
	poetry run flake8 app tests

# Remove Python cache files and pytest cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Run the FastAPI app in Docker Compose
docker-run:
	docker compose up --build api

# Run tests inside the Docker Compose container
docker-test:
	docker compose exec api poetry run pytest

# Clean and destroy the Docker Compose environment (containers, networks, volumes)
docker-clean:
	docker compose down -v --remove-orphans
