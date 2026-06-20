from datetime import timedelta

from django import template
from django.db.models import Q
from django.utils import timezone

from catalog.models import ConditionerOrder, ORDER_STATUS_IN_PROGRESS, ORDER_STATUS_NEW
from service.models import Order, ServiceOrder


register = template.Library()


@register.simple_tag
def get_order_dashboard():
    now = timezone.now()
    stale_before = now - timedelta(hours=24)

    orders = [Order.objects.all(), ServiceOrder.objects.all(), ConditionerOrder.objects.all()]
    new_count = sum(queryset.filter(status=ORDER_STATUS_NEW).count() for queryset in orders)
    in_progress_count = sum(queryset.filter(status=ORDER_STATUS_IN_PROGRESS).count() for queryset in orders)
    unassigned_count = sum(queryset.filter(manager__isnull=True).count() for queryset in orders)
    stale_count = sum(
        queryset.filter(
            Q(status__in=[ORDER_STATUS_NEW, ORDER_STATUS_IN_PROGRESS]) & Q(created_at__lt=stale_before)
        ).count()
        for queryset in orders
    )

    return {
        "new_count": new_count,
        "in_progress_count": in_progress_count,
        "unassigned_count": unassigned_count,
        "stale_count": stale_count,
    }
