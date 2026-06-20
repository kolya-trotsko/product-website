from django.contrib import admin
from django.utils.html import format_html
from .models import AirConditioner, Color, Company, Review, ConditionerOrder


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hash")
    search_fields = ("name", "hash")


@admin.register(AirConditioner)
class AirConditionerAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "price", "photo_preview")
    list_filter = ("company", "colors")
    search_fields = ("name", "company__name")
    list_select_related = ("company",)
    filter_horizontal = ("colors",)

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if not obj.photo:
            return "Немає"
        return format_html('<img src="{}" alt="{}" style="height:50px;"/>', obj.photo.url, obj.name)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("conditioner", "user", "rating")
    list_filter = ("rating", "conditioner")
    search_fields = ("user__username", "user__email", "conditioner__name")
    list_select_related = ("conditioner", "user")


@admin.register(ConditionerOrder)
class ConditionerOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "conditioner", "color")
    list_filter = ("conditioner", "color")
    search_fields = ("name", "phone", "address", "conditioner__name")
    list_select_related = ("conditioner", "color")
