from django.contrib import admin
from .models import CompanyInfo


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "address", "email", "phone", "instagram_link", "telegram_link", "viber_link"]
    list_display_links = ("id",)
    list_editable = ["address", "email", "phone", "instagram_link", "telegram_link", "viber_link"]
    search_fields = ("address", "email", "phone")

    def has_add_permission(self, request):
        if CompanyInfo.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False
