from django.conf import settings
from company_info.models import CompanyInfo


def site_metadata(request):
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    if not site_url and request is not None:
        site_url = f"{request.scheme}://{request.get_host()}"

    canonical_url = ""
    if site_url and request is not None:
        canonical_url = f"{site_url}{request.path}"

    return {
        "site_name": getattr(settings, "SITE_NAME", "KS KLIMAT KH"),
        "site_url": site_url,
        "canonical_url": canonical_url,
        "default_seo_image": f"{site_url}{settings.MEDIA_URL}logos/ks_klimat_kh.PNG" if site_url else "",
        "default_seo_description": (
            "KS KLIMAT KH: чистка, ремонт, сервіс і продаж кондиціонерів у Харкові. "
            "Консультація, виїзд майстра та підбір кондиціонера під приміщення."
        ),
    }


def company_contacts(request):
    contacts = CompanyInfo.objects.first()
    phone = contacts.phone.strip() if contacts and contacts.phone else ""
    phone_digits = "".join(char for char in phone if char.isdigit())
    phone_href = f"+{phone_digits}" if phone.startswith("+") else phone_digits
    phone_display = phone

    if phone_digits.startswith("380") and len(phone_digits) == 12:
        phone_display = f"+380 {phone_digits[3:5]} {phone_digits[5:8]} {phone_digits[8:10]} {phone_digits[10:12]}"
    elif phone_digits.startswith("0") and len(phone_digits) == 10:
        phone_display = f"{phone_digits[0:3]} {phone_digits[3:6]} {phone_digits[6:8]} {phone_digits[8:10]}"

    return {
        "header_contacts": contacts,
        "header_phone": phone_display,
        "header_phone_href": phone_href,
    }
