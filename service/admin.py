from django.contrib import admin
from .models import AirConditioningService, Order, ServiceOrder


@admin.register(AirConditioningService)
class AirConditioningServiceAdmin(admin.ModelAdmin):
    list_display = ("service_name", "service_price")
    search_fields = ("service_name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "place")
    search_fields = ("name", "phone", "place")


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "place", "address")
    search_fields = ("name", "phone", "place", "address")
