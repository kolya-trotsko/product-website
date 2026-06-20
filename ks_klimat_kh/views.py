from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    if not site_url:
        site_url = f"{request.scheme}://{request.get_host()}"

    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /telegram/",
        f"Sitemap: {site_url}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
