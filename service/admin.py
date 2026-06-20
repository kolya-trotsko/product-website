from django.contrib import admin

from ks_klimat_kh.admin_mixins import AssignmentFilter, FreshnessFilter, OrderWorkflowAdminMixin

from .models import AirConditioningService, BotLead, Order, ServiceOrder


@admin.register(AirConditioningService)
class AirConditioningServiceAdmin(admin.ModelAdmin):
    list_display = ("service_name", "service_price")
    search_fields = ("service_name",)


@admin.register(Order)
class OrderAdmin(OrderWorkflowAdminMixin, admin.ModelAdmin):
    list_display = ("status_badge", "status", "created_at", "name", "phone_link", "place", "manager", "age_display")
    list_display_links = ("name",)
    list_editable = ("status", "manager")
    list_filter = ("status", AssignmentFilter, FreshnessFilter, "manager", "created_at")
    search_fields = ("name", "phone", "place", "source_page", "admin_comment")
    list_select_related = ("manager",)
    fieldsets = (
        ("Client", {"fields": ("name", "phone", "place")}),
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


@admin.register(ServiceOrder)
class ServiceOrderAdmin(OrderWorkflowAdminMixin, admin.ModelAdmin):
    list_display = ("status_badge", "status", "created_at", "name", "phone_link", "place", "address", "manager", "age_display")
    list_display_links = ("name",)
    list_editable = ("status", "manager")
    list_filter = ("status", AssignmentFilter, FreshnessFilter, "manager", "created_at")
    search_fields = ("name", "phone", "place", "address", "source_page", "admin_comment")
    list_select_related = ("manager",)
    fieldsets = (
        ("Client", {"fields": ("name", "phone", "address", "place")}),
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


@admin.register(BotLead)
class BotLeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "intent", "telegram_user_id", "telegram_username", "full_name", "status", "manager")
    list_filter = ("intent", "status", "manager", "created_at")
    search_fields = ("telegram_username", "full_name", "message", "telegram_user_id")
    list_editable = ("status", "manager")
    list_display_links = ("telegram_user_id",)
