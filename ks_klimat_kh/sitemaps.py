from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from catalog.models import AirConditioner


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "service", "catalog"]

    def location(self, item):
        return reverse(item)


class AirConditionerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return AirConditioner.objects.filter(is_in_stock=True).select_related("company").order_by("id")

    def location(self, item):
        return reverse("conditioner_detail", args=[item.id])
