from django.conf import settings


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
