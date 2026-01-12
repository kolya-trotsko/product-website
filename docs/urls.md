# URLs

## Root router
File: ks_klimat_kh/urls.py
- /admin/ -> Django admin
- / -> redirect to /service/home/
- /catalog/ -> catalog app
- /service/ -> service app

Static and media routes are added via django.conf.urls.static for development.

## catalog app
File: catalog/urls.py
- /catalog/ -> catalog view
- /catalog/<conditioner_id>/ -> conditioner_detail view
- /catalog/<conditioner_id>/review/ -> add_review view

## service app
File: service/urls.py
- /service/ -> service view
- /service/home/ -> home view
- /service/policy/ -> policy view
