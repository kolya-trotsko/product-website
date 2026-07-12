from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from ks_klimat_kh.models import NotificationOutbox
from ks_klimat_kh.telegram_notify import TelegramDeliveryError, send_message


class Command(BaseCommand):
    help = "Send pending notification outbox rows."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        sent = 0
        failed = 0
        for notification in self._claim_pending(options["limit"]):
            try:
                send_message(notification.payload["text"])
            except (KeyError, TelegramDeliveryError) as exc:
                notification.mark_failed(exc)
                failed += 1
            else:
                with transaction.atomic():
                    self._mark_related_reminder(notification)
                    notification.mark_sent()
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"Outbox processed: sent={sent}, failed={failed}"))

    def _claim_pending(self, limit):
        now = timezone.now()
        with transaction.atomic():
            queryset = NotificationOutbox.objects.filter(
                status=NotificationOutbox.STATUS_PENDING,
                next_attempt_at__lte=now,
            ).order_by("created_at")
            if connection.features.has_select_for_update:
                queryset = queryset.select_for_update(skip_locked=connection.features.has_select_for_update_skip_locked)
            notifications = list(queryset[:limit])
            ids = [notification.id for notification in notifications]
            if ids:
                NotificationOutbox.objects.filter(
                    id__in=ids,
                    status=NotificationOutbox.STATUS_PENDING,
                ).update(status=NotificationOutbox.STATUS_PROCESSING, updated_at=now)
            for notification in notifications:
                notification.status = NotificationOutbox.STATUS_PROCESSING
            return notifications

    def _mark_related_reminder(self, notification):
        model_label = notification.payload.get("model_label")
        object_id = notification.payload.get("object_id")
        reminder_field = notification.payload.get("reminder_field")
        if not (model_label and object_id and reminder_field):
            return
        try:
            app_label, model_name = model_label.split(".", 1)
            model = apps.get_model(app_label, model_name)
        except (LookupError, ValueError):
            return
        if not hasattr(model, reminder_field):
            return
        model.objects.filter(id=object_id, **{f"{reminder_field}__isnull": True}).update(
            **{
                reminder_field: timezone.now(),
                "updated_at": timezone.now(),
            }
        )
