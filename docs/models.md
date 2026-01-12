# Models

## catalog
- Company: name, logo
- Color: name, hash
- AirConditioner: name, price, photo, description, company(FK), colors(M2M)
- Review: conditioner(FK), user, text, rating
- ConditionerOrder: name, phone, address, conditioner(FK), color(FK)

## service
- AirConditioningService: service_name, service_price
- Order: name, phone, place
- ServiceOrder: name, phone, place, address

## company_info
- CompanyInfo: address, email, phone, instagram_link, telegram_link, viber_link

Notes:
- Some verbose_name strings in models appear garbled (likely file encoding issue). Check source if you need to fix labels.
