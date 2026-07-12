from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review
from .ratings import recalculate_product_rating


@receiver(post_save, sender=Review)
def update_product_rating_after_review_save(sender, instance, **kwargs):
    recalculate_product_rating(instance.conditioner_id)


@receiver(post_delete, sender=Review)
def update_product_rating_after_review_delete(sender, instance, **kwargs):
    recalculate_product_rating(instance.conditioner_id)
