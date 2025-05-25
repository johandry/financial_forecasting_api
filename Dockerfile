FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY ./app ./app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]