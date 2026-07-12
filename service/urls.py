from django.urls import path

from .views import home, policy, service

urlpatterns = [
    path("", service, name="service"),
    path("home/", home, name="home"),
    path("policy/", policy, name="policy"),
]
