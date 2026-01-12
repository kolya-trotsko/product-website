# company_info app

## Purpose
Store a single set of contact details used across pages.

## Model
File: company_info/models.py
- CompanyInfo: address, email, phone, instagram_link, telegram_link, viber_link
- save() raises an exception if a second record is added

## Admin
File: company_info/admin.py
- list_display and list_editable expose all fields
- add and delete actions are restricted to enforce a single row

## Usage
- company_info is referenced by catalog and service views to populate contact blocks in templates
