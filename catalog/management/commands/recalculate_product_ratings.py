from django.core.management.base import BaseCommand

from catalog.models import CatalogProduct
from catalog.ratings import recalculate_product_rating


class Command(BaseCommand):
    help = "Recalculate cached average rating and review count for catalog products."

    def handle(self, *args, **options):
        count = 0
        for product_id in CatalogProduct.objects.values_list("id", flat=True).iterator():
            recalculate_product_rating(product_id)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Recalculated ratings for {count} products."))
