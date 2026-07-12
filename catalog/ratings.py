from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Avg, Count

from .models import CatalogProduct, Review


def recalculate_product_rating(product_id):
    rating = Review.objects.filter(conditioner_id=product_id, rating__isnull=False, is_superseded=False).aggregate(
        avg=Avg("rating"), count=Count("id")
    )
    rating_count = rating["count"] or 0
    rating_avg = None
    if rating_count:
        rating_avg = Decimal(str(rating["avg"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    CatalogProduct.objects.filter(id=product_id).update(
        rating_avg=rating_avg,
        rating_count=rating_count,
    )
