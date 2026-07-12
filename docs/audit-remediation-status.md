# Audit Remediation Status

| ID | Priority | Audit finding | Verification result | Files involved | Chosen fix | Tests added | Final status |
|---|---|---|---|---|---|---|---|
| P0.1 | P0 | Production settings could start unsafely | Confirmed | `ks_klimat_kh/settings.py`, `.env.example` | Added fail-closed validation for `SECRET_KEY`, `ALLOWED_HOSTS`, `SITE_URL`, Redis, HSTS/proxy options | `ProductionSettingsTests` | Implemented |
| P0.2 | P0 | Deprecated `STATICFILES_STORAGE` | Confirmed | `ks_klimat_kh/settings.py`, `requirements.txt` | Replaced with `STORAGES`; upgraded WhiteNoise; collectstatic verified | Baseline/static verification | Implemented |
| P0.3 | P0 | PostgreSQL driver missing | Confirmed | `requirements.txt`, `README.md` | Added `psycopg[binary]`; documented PostgreSQL/SQLite split | CI/deploy docs | Implemented |
| P0.4 | P0 | Telegram delivery synchronous/unreliable | Confirmed | `ks_klimat_kh/models.py`, `telegram_notify.py`, `process_notification_outbox.py`, views, migrations | Added database outbox, typed delivery errors, retry worker, dedupe keys, completion-based reminders | Outbox/reminder/order tests | Implemented |
| P0.5 | P0 | Rate limiting not production-safe | Confirmed | `settings.py`, `rate_limit.py`, views | Added Redis requirement in production, atomic cache add/incr flow, trusted proxy guard, `Retry-After` | `test_rate_limit_returns_retry_after` | Implemented |
| P0.6 | P0 | Review endpoint accepted unsafe flows | Confirmed | `catalog/views.py`, `catalog/models.py` | Added `require_POST`, auth checks, duplicate guard, DB constraints | Review endpoint tests | Implemented |
| P0.7 | P0 | Empty required color select | Confirmed | `catalog/forms.py`, product detail template | Color select renders only when required; backend accepts no-color products | Product-without-colors test | Implemented |
| P0.8 | P0 | Invalid modal errors hidden | Confirmed | product/service/home templates, `popup.js`, `base.css` | Modal opens on errors, visible summary, focus target | Existing/new form tests cover rendered errors partially | Implemented |
| P1.1 | P1 | Review invariants only in forms | Confirmed | `catalog/models.py`, migration `0012` | Rating check constraint, timestamps, conditional uniqueness with deterministic duplicate superseding | DB rating and duplicate tests | Implemented |
| P1.2 | P1 | Public product query duplicated | Confirmed | `catalog/models.py`, views, sitemap | Added `CatalogProduct.objects.public()` and applied to public paths | Visibility covered in existing catalog tests | Implemented |
| P1.3 | P1 | Comparison order unstable | Confirmed | `catalog/views.py` | Sort query result by selected ID order | Existing compare coverage updated | Implemented |
| P1.4 | P1 | Price/image ORM cleanup | Confirmed partially | `catalog/models.py` | Not completed beyond existing prefetch use | None | Backlog P1 |
| P1.5 | P1 | Duplicated phone validation | Confirmed | `ks_klimat_kh/validators.py`, forms | Shared validator with stricter punctuation/digit checks | Existing form tests | Implemented |
| P1.6 | P1 | Service order services stored as text | Confirmed | `service/models.py`, forms/views | Not completed; requires broader data-model migration | None | Backlog P1 |
| P1.7 | P1 | Status transitions scattered | Confirmed | `order_status.py`, admin, webhook, models | Added transition helper and model lifecycle for `completed_at` | Reminder/order tests | Implemented |
| P1.8 | P1 | Telegram webhook security/idempotency | Confirmed | `telegram_bot.py`, `ks_klimat_kh/models.py` | Secret header/path constant-time check, `update_id` persistence, size/JSON validation, active staff assignment | Webhook tests | Implemented |
| P1.9 | P1 | Logging/error handling/health | Confirmed | `settings.py`, `views.py`, URLs, error templates | Added console logging, custom handlers, `/healthz/` | Error/health tests | Implemented |
| P1.10 | P1 | CI missing | Confirmed | `.github/workflows/ci.yml`, `pyproject.toml`, `requirements-dev.txt` | Added GitHub Actions quality gates | CI config | Implemented |
| P1.11 | P1 | README/hygiene gaps | Confirmed | `README.md`, `.gitignore`, `AGENTS.md` | Added docs and ignored runtime artifacts; unignored `docs/` | Documentation review | Implemented |
| P1.12 | P1 | Deployment not reproducible | Confirmed | `README.md`, `Procfile`, `.env.example` | Documented web/migrate/static/worker/scheduler/envs; added worker process | Deployment check | Implemented |
| P2.1 | P2 | JSON-LD could emit invalid offer | Confirmed | `seo.py`, sitemap | Offer only when price/currency exist; sitemap lastmod/public rules | SEO schema tests | Implemented |
| P2.2 | P2 | SEO slug URLs | Already fixed partially | `CatalogProduct.slug` exists | Canonical slug routes not implemented in this pass | None | Backlog P2 |
| P2.3 | P2 | Modal accessibility incomplete | Confirmed | templates, `popup.js` | Added dialog semantics, error focus, Escape close; full focus trap not completed | Partial | Backlog P2 |
| P2.4 | P2 | General accessibility improvements | Confirmed | templates/static | Not completed except modal/error-health related changes | None | Backlog P2 |
| P2.5 | P2 | Image/frontend performance | Confirmed | templates | Not completed; primary image still needs final performance pass | None | Backlog P2 |
| P2.6 | P2 | Privacy page stale | Confirmed | `service/templates/policy/policy.html` | Not completed | None | Backlog P2 |
| P3 | P3 | Portfolio presentation polish | Confirmed | `README.md`, `AGENTS.md`, this file | Added architecture diagram, decisions, checklists, metadata recommendation | Docs | Implemented partially |

## Baseline

- Global `python manage.py ...` failed because Django was not installed globally.
- Repository venv baseline passed `check`, `makemigrations --check --dry-run`, `test`, and `collectstatic`.
- `collectstatic` reports duplicate static destination warnings from multiple app static directories.
- Ruff/Bandit/pip-audit/coverage were not configured before this branch.

## Remaining Backlog

- P1: normalized `ServiceOrder` service items and structured service pricing.
- P1: deeper ORM/query-count regression tests for product price/image selection.
- P2: canonical slug routes with permanent redirects from numeric product URLs.
- P2: full modal focus trap and broader accessibility pass.
- P2: privacy policy factual update and legal review.
- P2: image loading/performance audit and post-deployment Lighthouse checklist.
- P3: real screenshots and repository About settings in GitHub UI.

## Final Verification

Executed with `.\venv\Scripts\python.exe` / repo virtualenv:

- `python manage.py check`: passed.
- `python manage.py makemigrations --check --dry-run`: passed.
- `python manage.py migrate`: passed, no pending migrations.
- Fresh temporary SQLite migration from zero: passed.
- `python manage.py test`: passed, 39 tests.
- `python manage.py collectstatic --noinput`: passed; duplicate static destination warnings remain from existing static layout.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `bandit -r catalog service ks_klimat_kh company_info -x migrations,tests`: passed.
- `pip-audit -r requirements.txt`: passed, no known vulnerabilities.
- `coverage run manage.py test && coverage report`: passed, total coverage 82%.
- `git diff --check`: passed.
- `python manage.py check --deploy`: passed cleanly when `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` and `SECURE_HSTS_PRELOAD=True`; with defaults it exits 0 but reports the expected opt-in HSTS warnings.
