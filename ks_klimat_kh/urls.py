from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from ks_klimat_kh.sitemaps import AirConditionerSitemap, StaticViewSitemap
from ks_klimat_kh.telegram_bot import telegram_webhook
from ks_klimat_kh.views import robots_txt


sitemaps = {
    "static": StaticViewSitemap,
    "conditioners": AirConditionerSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/service/home/')),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path('accounts/', include('allauth.urls')),
    path('catalog/', include('catalog.urls')),
    path('service/', include('service.urls')),
    path("telegram/webhook/<str:secret>/", telegram_webhook, name="telegram_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
