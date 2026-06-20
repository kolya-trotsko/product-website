from django.db import models
from django.conf import settings
from .apps import CatalogConfig
from django.utils.translation import gettext_lazy as _


app_name = CatalogConfig.name


class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', default=None, null=True, blank=True)

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
    photo = models.ImageField(upload_to=app_name + '/air_conditioner_photos/')
    description = models.TextField()
    colors = models.ManyToManyField(Color, blank=True, related_name='air_conditioners')
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

    def __str__(self):
        return self.name
