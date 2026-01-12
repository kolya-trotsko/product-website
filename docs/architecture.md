# Architecture

## Project layout
- ks_klimat_kh/: Django project (settings, urls, wsgi/asgi, base templates)
- catalog/: product catalog app
- service/: service and homepage app
- company_info/: single-row contact info app
- media/: uploaded images and assets

## Settings highlights
- Django version in requirements.txt: 4.2.7
- Installed apps: catalog, service, company_info, ks_klimat_kh
- Templates: project-level templates in ks_klimat_kh/templates and app templates via APP_DIRS
- Static files: STATICFILES_DIRS is built from each app's static folder
- Media: MEDIA_ROOT=media, MEDIA_URL=/media/
- Whitenoise is enabled for static file serving

## Request flow
- Root URL conf: ks_klimat_kh/urls.py
- Default route redirects to /service/home/

## Data storage
- SQLite database: db.sqlite3
- Media files stored under media/ (images, logos, catalog photos)

## Admin
- company_info uses a singleton pattern and custom admin rules to prevent multiple records
