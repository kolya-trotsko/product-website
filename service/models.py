from django.conf import settings
from django.db import models


ORDER_STATUS_NEW = "new"
ORDER_STATUS_IN_PROGRESS = "in_progress"
ORDER_STATUS_DONE = "done"
ORDER_STATUS_CANCELLED = "cancelled"

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_NEW, "New"),
    (ORDER_STATUS_IN_PROGRESS, "In progress"),
    (ORDER_STATUS_DONE, "Done"),
    (ORDER_STATUS_CANCELLED, "Cancelled"),
]


class AirConditioningService(models.Model):
    service_name = models.CharField(max_length=100)
    service_price = models.CharField(max_length=100)

    def __str__(self):
        return self.service_name


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    place = models.CharField(max_length=100, verbose_name="Послуга")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_NEW, db_index=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="home_orders",
    )
    admin_comment = models.TextField(blank=True, default="")
    source_page = models.CharField(max_length=100, blank=True, default="", db_index=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    place = models.CharField(max_length=100, verbose_name="Послуги", null=True, default="")
    address = models.CharField(max_length=100, verbose_name="Адреса")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_NEW, db_index=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_orders",
    )
    admin_comment = models.TextField(blank=True, default="")
    source_page = models.CharField(max_length=100, blank=True, default="", db_index=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
