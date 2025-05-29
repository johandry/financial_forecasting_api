.PHONY: run install test clean seed dc-run dc-test dc-seed lint

# Install all dependencies
install:
	poetry install

# Run the FastAPI app (dev mode)
run-backend:
	ENV=local poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

# Run tests
test:
	ENV=test poetry run pytest # -vv

# Seed the database with data from seed_data.yaml
seed:
	docker compose up --detach api db
	docker compose cp seed_data.yaml api:/app/seed_data.yaml
	docker compose exec -e PYTHONPATH=. api poetry run python app/core/seed.py /app/seed_data.yaml


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
	rm -f test.db

# Run the FastAPI app in Docker Compose
docker-run:
	open http://localhost:5173
	docker compose up --build api db redis # frontend 

# Run tests inside the Docker Compose container
docker-test:
	docker compose exec api poetry run pytest

# Clean and destroy the Docker Compose environment (containers, networks, volumes)
docker-clean:
	docker compose down -v --remove-orphans

# Clean up Docker Compose environment and remove Python generated files
nuke: docker-clean clean
	docker image rm financial_forecasting_api-api:latest || true
	docker image rm financial_forecasting_api-frontend:latest || true
	docker images