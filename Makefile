.PHONY: run install test clean seed dc-run dc-test dc-seed

# Install all dependencies
install:
	poetry install

# Run the FastAPI app (dev mode)
run:
	ENV=local poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	docker compose up -d redis
	ENV=local poetry run pytest

# Seed the database with test data
seed:
	ENV=local PYTHONPATH=. poetry run python app/core/seed.py

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

# Seed the database inside the Docker Compose container
docker-seed:
	docker compose exec api poetry run python app/core/seed.py