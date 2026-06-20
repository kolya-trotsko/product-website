# Setup

## Requirements
- Python 3.x
- pip
- dependencies in requirements.txt

## Local install
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Database
```bash
python manage.py migrate
```

## Superuser (admin)
```bash
python manage.py createsuperuser
```

## Run
```bash
python manage.py runserver
```

## Static collection (for deployment)
```bash
python manage.py collectstatic
```

Notes:
- Default database is sqlite: db.sqlite3
- MEDIA_ROOT is ./media and STATIC_ROOT is ./staticfiles

## Telegram notifications for new orders
Set these env vars (for example in `.env`):

```env
TELEGRAM_NOTIFICATIONS_ENABLED=True
TELEGRAM_BOT_TOKEN=123456:your_bot_token
TELEGRAM_ADMIN_CHAT_IDS=123456789,987654321
```

Notes:
- `TELEGRAM_ADMIN_CHAT_IDS` supports one or many chat IDs separated by comma.
- If telegram is unavailable, order creation still succeeds and warning is logged.
