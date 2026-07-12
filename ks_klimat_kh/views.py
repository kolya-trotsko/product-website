from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def healthz(request):
    return JsonResponse({"ok": True, "checks": {"web": "ok"}})


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


def bad_request(request, exception):
    return render(request, "errors/400.html", status=400)


def permission_denied(request, exception):
    return render(request, "errors/403.html", status=403)


def page_not_found(request, exception):
    return render(request, "errors/404.html", status=404)


def server_error(request):
    return render(request, "errors/500.html", status=500)
