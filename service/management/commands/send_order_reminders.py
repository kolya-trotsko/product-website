from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import ORDER_STATUS_DONE as C_DONE
from catalog.models import ORDER_STATUS_NEW as C_NEW
from catalog.models import ConditionerOrder
from ks_klimat_kh.telegram_notify import notify_service_cycle, notify_unaccepted_order
from service.models import (
    ORDER_STATUS_DONE as S_DONE,
)
from service.models import (
    ORDER_STATUS_NEW as S_NEW,
)
from service.models import (
    Order,
    ServiceOrder,
)


class Command(BaseCommand):
    help = "Send Telegram reminders for unaccepted and post-sale service cycles."

    def add_arguments(self, parser):
        parser.add_argument("--hours-unaccepted", type=int, default=2)

    def handle(self, *args, **options):
        now = timezone.now()
        threshold = now - timedelta(hours=options["hours_unaccepted"])
        sent = 0

        sent += self._notify_unaccepted(Order, "home", S_NEW, threshold)
        sent += self._notify_unaccepted(ServiceOrder, "service", S_NEW, threshold)
        sent += self._notify_unaccepted(ConditionerOrder, "catalog", C_NEW, threshold)

        sent += self._notify_service_cycle(Order, "home", S_DONE, now)
        sent += self._notify_service_cycle(ServiceOrder, "service", S_DONE, now)
        sent += self._notify_service_cycle(ConditionerOrder, "catalog", C_DONE, now)

        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent}"))

    def _notify_unaccepted(self, model, order_type, status_new, threshold):
        count = 0
        queryset = model.objects.filter(
            status=status_new,
            created_at__lte=threshold,
            unaccepted_reminded_at__isnull=True,
        )[:100]
        for order in queryset:
            notify_unaccepted_order(order_type, order)
            count += 1
        return count

    def _notify_service_cycle(self, model, order_type, status_done, now):
        count = 0
        six_months = now - timedelta(days=180)
        twelve_months = now - timedelta(days=365)

        for order in model.objects.filter(
            status=status_done,
            completed_at__lte=twelve_months,
            service_reminder_12m_sent_at__isnull=True,
        )[:100]:
            notify_service_cycle(order_type, order, 12)
            count += 1

        for order in model.objects.filter(
            status=status_done,
            completed_at__lte=six_months,
            completed_at__gt=twelve_months,
            service_reminder_6m_sent_at__isnull=True,
        )[:100]:
            notify_service_cycle(order_type, order, 6)
            count += 1

        return count
