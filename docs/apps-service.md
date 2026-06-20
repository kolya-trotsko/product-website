# service app

## Purpose
Homepage, service listing, and policy page with order capture forms.

## Models
File: service/models.py
- AirConditioningService
- Order
- ServiceOrder

## Views
File: service/views.py
- home: shows companies; creates Order on POST
- service: lists services; creates ServiceOrder on POST
- policy: renders policy page

Note: service.view validates order input through forms and stores selected services as a comma-separated value in ServiceOrder.place.

## URLs
File: service/urls.py
- /service/
- /service/home/
- /service/policy/

## Templates and static
- service/templates/home/home.html
- service/templates/service/service.html
- service/templates/policy/policy.html
- service/static/css/home/home.css
- service/static/css/service/service.css
- service/static/css/policy/policy.css
- service/static/js/home.js
- ks_klimat_kh/static/js/popup.js
