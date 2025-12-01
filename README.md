# Export User Info API

## Features
- REST API for listing users with pagination, organization filters, and dynamic
  column selection driven by each organization's `org_config`.
- Aggregated filter endpoints (locations, departments, positions,
  organizations) for UI dropdowns/autocomplete.
- Sliding-window rate limiting middleware with configurable request limits.
- Alembic migration history plus `seed` command that generates sample
  organizations and users.
- Dockerfile + `docker-compose.yaml` for one-command local environments.

## Tech Stack
- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy 2.x ORM + Alembic migrations
- PostgreSQL (psycopg2 driver)
- Faker for deterministic sample data

## Repository Layout
```
export-user-info/
├── docker-compose.yaml        # API + Postgres development stack
├── requirements.txt           # Python dependencies
├── src/
│   ├── main.py                # Entry point (run server or seed data)
│   ├── api/                   # FastAPI routers (`/api/v1/users`)
│   ├── config/                # App factory, rate limiter settings
│   ├── middleware/            # Sliding window rate limiter
│   ├── services/              # User list & filter business logic
│   ├── models/, schemas/      # SQLAlchemy models & Pydantic DTOs
│   ├── db/                    # Engine factory & Alembic setup
│   └── seed.py                # Faker data generators
└── src/alembic/               # Migration environment & revisions
```

## Requirements
- Python 3.12+
- PostgreSQL 14+ (local install or Docker)
- `pip`, `virtualenv` (or any environment manager)

## Configuration
Settings are loaded from environment variables (via `.env`). Create a file in
the project root when using Docker or `src/.env` when using local environment:

```bash
APP_NAME=Export User Info
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
LIMIT=25                   # Requests allowed per window
WINDOW_TIME=10             # Window size in seconds
DB_HOST=localhost
DB_PORT=5432
DB_USER=root
DB_PASSWORD=example
DB_NAME=user_management
```

## Local Development
```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start Postgres (optional helper using compose)
docker compose up db -d

# Apply database schema
cd src
alembic upgrade head

# Generate demo data
python main.py seed

# Run the API (http://localhost:8000/docs)
python main.py
```

> Tip: keep `src` as the working directory when running CLI commands so Python
> imports resolve correctly.

## Running Tests
The repo includes API and rate limiter coverage powered by pytest. From the project
root run:

```bash
./venv/bin/pytest
```

If you use a different virtual environment path, swap the interpreter accordingly
(`python -m pytest` works when `pytest` is installed in the active env).

## Docker Workflow
```bash
docker compose up --build
```
The compose file starts both the API (port `8000`) and a PostgreSQL instance
(port `5432`). Place production-ready environment variables inside `.env` or
`src/.env`; both are loaded automatically.

## Database Migrations & Seeding
- Create new migrations from `src/`: `alembic revision --autogenerate -m "msg"`
- Apply migrations: `alembic upgrade head`
- Populate demo organizations/users: `python main.py seed`

The seed script inserts 10 organizations with custom `org_config` JSON plus
~5,000 users (500 per organization) to showcase pagination and filtering.

## API Overview

| Endpoint | Method | Description |
| --- | --- | --- |
| `/health` | GET | Liveness check. |
| `/api/v1/users` | GET | Paginated user export with optional filters. |
| `/api/v1/users/filters` | GET | Lists distinct locations, departments, positions, organizations. |

### `GET /api/v1/users`
Query parameters (all optional except pagination defaults):

| Parameter | Type | Notes |
| --- | --- | --- |
| `limit` | int | Page size (1-100, default 100). |
| `offset` | int | Results offset (default 0). |
| `status` | list[str] | Accepted values: `ACTIVE`, `TERMINATED`, `NOT_STARTED`. |
| `location` | str | Filter by matching location (if enabled for the organization). |
| `department` | str | Filter by department. |
| `position` | str | Filter by position. |
| `org_id` | int | Restrict to a specific organization and honor its `org_config`. |

Response
```json
{
  "total_page": 50,
  "page": 1,
  "count": 5000,
  "data": [
    {
      "id": 1,
      "first_name": "Ada",
      "last_name": "Lovelace",
      "email": "ada@example.com",
      "location": "United States",
      "org_id": 3
    }
  ]
}
```

### `GET /api/v1/users/filters`
Returns distinct values for each filter plus full organization records so a
front end can build dropdowns quickly. Results are cached in-memory inside the
service layer via `functools.lru_cache`.

### Rate Limiting
All endpoints pass through the sliding window middleware
(`src/middleware/rate_limiter.py`). Defaults are `10` requests per `10` seconds
per client IP + path, and can be tuned via `LIMIT` and `WINDOW_TIME`. Responses
include standard `X-RateLimit-*` headers plus `Retry-After` on 429 errors.

## Development Tips
- Interactive docs are available at `http://localhost:8000/docs` (Swagger UI)
  and `/redoc`.
- Logs stream to STDOUT using the configured `LOG_LEVEL`.
- When you change Pydantic models or SQLAlchemy metadata, regenerate and run
  migrations so the API and database stay aligned.

Happy exporting!
