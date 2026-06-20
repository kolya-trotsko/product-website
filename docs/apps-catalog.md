# catalog app

## Purpose
Product catalog for air conditioners with filtering, detail view, reviews, and order creation.

## Models
File: catalog/models.py
- Company
- Color
- AirConditioner (FK to Company, M2M to Color)
- Review (FK to AirConditioner)
- ConditionerOrder (FK to AirConditioner and Color)

## Views
File: catalog/views.py
- catalog: search by name, filter by color/company, paginate (15 per page)
- conditioner_detail: show details and reviews; creates ConditionerOrder on POST
- add_review: validates ReviewForm and saves review

## Forms
File: catalog/forms.py
- ReviewForm: text, rating, user

## URLs
File: catalog/urls.py
- /catalog/
- /catalog/<conditioner_id>/
- /catalog/<conditioner_id>/review/

## Templates and static
- catalog/templates/catalog/catalog.html
- catalog/templates/catalog/conditioner_detail.html
- catalog/static/css/catalog.css
- catalog/static/css/conditioner_detail.css
- catalog/static/js/catalog.js
- ks_klimat_kh/static/js/popup.js
