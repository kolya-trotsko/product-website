from django.conf import settings
from django.db import models

from .apps import CatalogConfig


app_name = CatalogConfig.name

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


class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/", default=None, null=True, blank=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)
    hash = models.CharField(max_length=100, null=True, default=None)

    def __str__(self):
        return self.name


class AirConditioner(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to=app_name + "/air_conditioner_photos/")
    description = models.TextField()
    colors = models.ManyToManyField(Color, blank=True, related_name="air_conditioners")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Review(models.Model):
    conditioner = models.ForeignKey(AirConditioner, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(null=True)

    def __str__(self):
        return f"Review: {self.user.get_username()} ({self.conditioner})"


class ConditionerOrder(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    address = models.CharField(max_length=100, verbose_name="Адреса")
    conditioner = models.ForeignKey(AirConditioner, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_NEW, db_index=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conditioner_orders",
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
