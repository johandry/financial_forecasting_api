# Financial Forecasting API

A Python-based backend service for ingesting bills and transactions, forecasting daily balances, and alerting users when projected balances fall below a configurable buffer. Built with FastAPI, SQLAlchemy, PostgreSQL, Redis, and Docker Compose.

---

## Features

- **CRUD** for accounts, bills, transactions, and user settings
- **Recurrence engine** for bills and transactions
- **Forecasting** of daily balances with buffer alerts
- **JWT authentication** (OAuth2 password flow)
- **Rate limiting** (100 req/min/user)
- **Soft-delete** and audit logging
- **CSV upload** and Excel export (planned)
- **Docker Compose** for local development

---

## Project Structure

```tree
financial_forecasting_api/
├── app/
│   ├── api/                # FastAPI routers
│   ├── core/               # Config, security, database, seed
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── crud.py             # CRUD logic
│   └── main.py             # FastAPI entrypoint
├── tests/                  # Pytest tests
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── .env
```

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/) (for local dev)

### Local Development

1. **Install dependencies:**

   ```bash
   poetry install
   ```

2. **Copy and edit `.env`:**

   ```bash
   cp .env.example .env
   # Edit as needed
   ```

3. **Run the app:**

   ```bash
   make run
   ```

4. **Seed the database:**

   ```bash
   make seed
   ```

5. **Run tests:**

   ```bash
   make test
   ```

### Docker Compose

1. **Start all services:**

   ```bash
   make docker-run
   ```

2. **Seed the database in Docker:**

   ```bash
   make docker-seed
   ```

3. **Run tests in Docker:**

   ```bash
   make docker-test
   ```

---

## API Endpoints

- `POST   /auth/login`
- `POST   /accounts`
- `GET    /accounts`
- `POST   /bills`
- `GET    /bills`
- `POST   /transactions`
- `GET    /transactions`
- `GET    /user_settings`
- `PUT    /user_settings`
- ...and more

See [OpenAPI docs](http://localhost:8000/docs) when running locally.

---

## License

Apache License 2.0

---
