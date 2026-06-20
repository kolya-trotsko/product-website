from django.contrib import admin
from django.utils.html import format_html

from ks_klimat_kh.admin_mixins import AssignmentFilter, FreshnessFilter, OrderWorkflowAdminMixin

from .models import AirConditioner, Color, Company, ConditionerOrder, Review


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
    list_display = (
        "name",
        "company",
        "conditioner_type",
        "recommended_area_m2",
        "warranty_months",
        "is_in_stock",
        "price",
        "photo_preview",
    )
    list_filter = ("company", "conditioner_type", "is_in_stock", "warranty_months", "colors")
    search_fields = ("name", "company__name", "country", "energy_class")
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
class ConditionerOrderAdmin(OrderWorkflowAdminMixin, admin.ModelAdmin):
    list_display = (
        "status_badge",
        "status",
        "created_at",
        "name",
        "phone_link",
        "conditioner",
        "color",
        "manager",
        "age_display",
    )
    list_display_links = ("name",)
    list_editable = ("status", "manager")
    list_filter = ("status", AssignmentFilter, FreshnessFilter, "conditioner", "color", "manager", "created_at")
    search_fields = ("name", "phone", "address", "conditioner__name", "source_page", "admin_comment")
    list_select_related = ("conditioner", "color", "manager")
    fieldsets = (
        ("Client", {"fields": ("name", "phone", "address")}),
        ("Order", {"fields": ("conditioner", "color")}),
        ("Workflow", {"fields": ("status", "manager", "admin_comment")}),
        (
            "Meta",
            {
                "fields": (
                    "source_page",
                    "client_ip",
                    "unaccepted_reminded_at",
                    "service_reminder_6m_sent_at",
                    "service_reminder_12m_sent_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
