from django.contrib import admin
from .models import AirConditioningService, Order, ServiceOrder


admin.site.register(AirConditioningService)
admin.site.register(Order)
admin.site.register(ServiceOrder)
