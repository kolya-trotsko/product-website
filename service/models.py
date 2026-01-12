from django.db import models


class AirConditioningService(models.Model):
    service_name = models.CharField(max_length=100)
    service_price = models.CharField(max_length=100)

    def __str__(self):
        return self.service_name


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name="??'?")
    phone = models.CharField(max_length=100, verbose_name="???????")
    place = models.CharField(max_length=100, verbose_name="??? ???????")

    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    name = models.CharField(max_length=100, verbose_name="??'?")
    phone = models.CharField(max_length=100, verbose_name="???????")
    place = models.CharField(max_length=100, verbose_name="??? ???????", null=True, default="")
    address = models.CharField(max_length=100, verbose_name="??????")

    def __str__(self):
        return self.name
