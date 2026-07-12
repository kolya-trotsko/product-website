from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from catalog.models import CatalogProduct


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "service", "catalog"]

    def location(self, item):
        return reverse(item)


class CatalogProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return CatalogProduct.objects.public().select_related("brand").order_by("id")

    def location(self, item):
        return reverse("conditioner_detail", args=[item.id])

    def lastmod(self, item):
        return item.updated_at
