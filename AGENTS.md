# AGENTS.md

## Architecture

KS KLIMAT KH is a Django 5.2 project with three main app areas:

- `catalog`: public product catalog, product detail pages, reviews, conditioner orders, ratings, product import metadata.
- `service`: home/service landing pages, service orders, reminder scheduler command, Telegram bot lead model.
- `ks_klimat_kh`: project settings, URLs, SEO helpers, sitemaps, rate limiting, Telegram delivery, notification outbox, health and error views.

External integrations are Google OAuth, Telegram Bot API, email, PostgreSQL, Redis, and optional persistent media storage.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
copy .env.example .env
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

## Test And Quality Commands

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe manage.py collectstatic --noinput
.\venv\Scripts\ruff.exe check .
.\venv\Scripts\ruff.exe format --check .
.\venv\Scripts\bandit.exe -r . -x migrations,venv,staticfiles,media
.\venv\Scripts\pip-audit.exe -r requirements.txt
git diff --check
```

Use safe temporary production values for `python manage.py check --deploy`.

## Migrations

- Create normal Django migrations for every schema change.
- Do not rewrite old migrations to make them prettier.
- Preserve existing rows; use deterministic data migrations for backfills.
- For unique constraints, handle existing conflicts before adding the constraint.
- Keep model changes and migrations in the same review unit.

## Security Rules

- Do not commit `.env`, real secrets, local databases, uploaded media, caches, or virtualenvs.
- Production must not run with placeholder `SECRET_KEY`, empty `ALLOWED_HOSTS`, or local-memory rate limiting.
- Mock Telegram, OAuth, email, Redis, storage, and other network boundaries in tests.
- Do not log tokens, passwords, OAuth secrets, Telegram bot tokens, or unnecessary personal-data payloads.
- Preserve local SQLite development when practical; use PostgreSQL and Redis for production.

## UI And Behavior Rules

- Preserve the existing Ukrainian UI text unless the change explicitly requires copy updates.
- Keep public URLs working unless a backward-compatible redirect is added.
- Update tests and documentation with every behavior change.
- For order lifecycle changes, use shared transition helpers so `completed_at` and timestamps stay consistent.
- Telegram notifications must go through the database outbox; HTTP requests must not call the live Telegram API.
