# 🛠️ Operations & Development Runbook

## Database Migrations (Alembic)

To generate and apply migrations in `apps/api`:

```bash
cd apps/api
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

## Running Celery Worker Locally

```bash
cd apps/worker
celery -A src.main.celery_app worker --loglevel=info
```

## ChromaDB Vector Store

ChromaDB runs locally at `http://localhost:8001` via `infra/docker-compose.yml`.
