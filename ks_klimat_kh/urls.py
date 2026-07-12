from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView

from ks_klimat_kh.sitemaps import CatalogProductSitemap, StaticViewSitemap
from ks_klimat_kh.telegram_bot import telegram_webhook
from ks_klimat_kh.views import healthz, robots_txt

sitemaps = {
    "static": StaticViewSitemap,
    "conditioners": CatalogProductSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/service/home/")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("healthz/", healthz, name="healthz"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("accounts/", include("allauth.urls")),
    path("catalog/", include("catalog.urls")),
    path("service/", include("service.urls")),
    path("telegram/webhook/<str:secret>/", telegram_webhook, name="telegram_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "ks_klimat_kh.views.bad_request"
handler403 = "ks_klimat_kh.views.permission_denied"
handler404 = "ks_klimat_kh.views.page_not_found"
handler500 = "ks_klimat_kh.views.server_error"
