from django.contrib import admin
from .models import AirConditioner, Color, Company, Review, ConditionerOrder


class ColorFilter(admin.SimpleListFilter):
    title = 'Color'
    parameter_name = 'color'

    def lookups(self, request, model_admin):
        return [(color.id, color.name) for color in Color.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(colors__id=self.value())
        else:
            return queryset


class AirConditionerAdmin(admin.ModelAdmin):
    list_filter = (ColorFilter,)
    filter_horizontal = ('colors',)  # Дозволить вибирати кілька кольорів зі списку


admin.site.register(AirConditioner, AirConditionerAdmin)
admin.site.register(Color)
admin.site.register(Company)
admin.site.register(Review)
admin.site.register(ConditionerOrder)
