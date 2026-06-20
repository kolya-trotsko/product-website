from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from ks_klimat_kh.telegram_bot import telegram_webhook


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/service/home/')),
    path('accounts/', include('allauth.urls')),
    path('catalog/', include('catalog.urls')),
    path('service/', include('service.urls')),
    path("telegram/webhook/<str:secret>/", telegram_webhook, name="telegram_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
