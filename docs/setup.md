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
