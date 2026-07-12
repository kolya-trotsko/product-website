from datetime import timedelta

from django.db import models
from django.utils import timezone


class NotificationOutbox(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    event_type = models.CharField(max_length=100, db_index=True)
    deduplication_key = models.CharField(max_length=255, unique=True)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    attempt_count = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=("status", "next_attempt_at")),
        ]

    def mark_sent(self):
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        self.last_error = ""
        self.save(update_fields=["status", "sent_at", "last_error", "updated_at"])

    def mark_failed(self, message):
        self.attempt_count += 1
        delay = min(60 * (2 ** max(self.attempt_count - 1, 0)), 3600)
        self.status = self.STATUS_PENDING
        self.next_attempt_at = timezone.now() + timedelta(seconds=delay)
        self.last_error = str(message)[:1000]
        self.save(
            update_fields=[
                "attempt_count",
                "status",
                "next_attempt_at",
                "last_error",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.event_type}: {self.deduplication_key}"


class TelegramUpdate(models.Model):
    update_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.update_id)
