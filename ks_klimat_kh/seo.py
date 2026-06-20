import json

from django.conf import settings
from django.db.models import Avg, Count


def safe_json_ld(data):
    return (
        json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003C")
        .replace(">", "\\u003E")
        .replace("&", "\\u0026")
    )


def absolute_url(request, path):
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    if not site_url:
        site_url = f"{request.scheme}://{request.get_host()}"
    return f"{site_url}{path}"


def local_business_schema(request, contacts=None):
    same_as = []
    if contacts:
        same_as = [
            url
            for url in [contacts.instagram_link, contacts.telegram_link, contacts.viber_link]
            if url
        ]

    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": getattr(settings, "SITE_NAME", "KS KLIMAT KH"),
        "url": absolute_url(request, "/"),
        "image": absolute_url(request, f"{settings.MEDIA_URL}logos/ks_klimat_kh.PNG"),
        "areaServed": {
            "@type": "City",
            "name": "Харків",
        },
        "priceRange": "₴₴",
    }

    if contacts:
        if contacts.phone:
            data["telephone"] = contacts.phone
        if contacts.email:
            data["email"] = contacts.email
        if contacts.address:
            data["address"] = {
                "@type": "PostalAddress",
                "streetAddress": contacts.address,
                "addressLocality": "Харків",
                "addressCountry": "UA",
            }
    if same_as:
        data["sameAs"] = same_as

    return safe_json_ld(data)


def product_schema(request, conditioner, reviews):
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": conditioner.name,
        "image": absolute_url(request, conditioner.photo.url if conditioner.photo else ""),
        "description": conditioner.description,
        "brand": {
            "@type": "Brand",
            "name": conditioner.company.name,
        },
        "offers": {
            "@type": "Offer",
            "url": absolute_url(request, request.path),
            "priceCurrency": "UAH",
            "price": str(conditioner.price),
            "availability": (
                "https://schema.org/InStock"
                if conditioner.is_in_stock
                else "https://schema.org/OutOfStock"
            ),
        },
    }

    rating = reviews.exclude(rating__isnull=True).aggregate(avg=Avg("rating"), count=Count("id"))
    if rating["count"]:
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(float(rating["avg"]), 1),
            "reviewCount": rating["count"],
        }

    return safe_json_ld(data)
