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
TELEGRAM_WEBHOOK_SECRET=long_random_secret
```

Notes:
- `TELEGRAM_ADMIN_CHAT_IDS` supports one or many chat IDs separated by comma.
- If telegram is unavailable, order creation still succeeds and warning is logged.
- Telegram webhook endpoint:
  `/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>/`
- Supported admin commands in bot (only for admin chat ids):
  `/new`, `/in_progress`, `/done`, `/assign <home|service|catalog> <order_id> <@username>`
- Supported lead intents in bot:
  `хочу консультацію`, `підібрати модель`

## Reminder jobs
Run periodically (for example each 15 minutes via scheduler):

```bash
python manage.py send_order_reminders --hours-unaccepted 2
```

This sends:
- reminder to managers/admin about unaccepted orders
- post-sale reminders after 6/12 months
