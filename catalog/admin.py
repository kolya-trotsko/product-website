from datetime import timedelta

from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    AirConditioner,
    Color,
    Company,
    ConditionerOrder,
    Review,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_DONE,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_NEW,
)


STATUS_BADGE_CLASS = {
    ORDER_STATUS_NEW: "status-new",
    ORDER_STATUS_IN_PROGRESS: "status-in-progress",
    ORDER_STATUS_DONE: "status-done",
    ORDER_STATUS_CANCELLED: "status-cancelled",
}


class AssignmentFilter(admin.SimpleListFilter):
    title = "Assignment"
    parameter_name = "assignment"

    def lookups(self, request, model_admin):
        return [
            ("unassigned", "Unassigned"),
            ("mine", "Assigned to me"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "unassigned":
            return queryset.filter(manager__isnull=True)
        if self.value() == "mine" and request.user.is_authenticated:
            return queryset.filter(manager=request.user)
        return queryset


class FreshnessFilter(admin.SimpleListFilter):
    title = "Freshness"
    parameter_name = "freshness"

    def lookups(self, request, model_admin):
        return [
            ("today", "New today"),
            ("stale", "Stale > 24h"),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "today":
            return queryset.filter(created_at__date=now.date())
        if self.value() == "stale":
            return queryset.filter(
                Q(status__in=[ORDER_STATUS_NEW, ORDER_STATUS_IN_PROGRESS])
                & Q(created_at__lt=now - timedelta(hours=24))
            )
        return queryset


class ConditionerOrderAdminMixin:
    date_hierarchy = "created_at"
    list_per_page = 50
    readonly_fields = ("created_at", "updated_at", "source_page", "client_ip")
    actions = ("mark_new", "mark_in_progress", "mark_done", "mark_cancelled")

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        css_class = STATUS_BADGE_CLASS.get(obj.status, "status-new")
        return format_html('<span class="status-badge {}">{}</span>', css_class, obj.get_status_display())

    @admin.display(description="Phone", ordering="phone")
    def phone_link(self, obj):
        return format_html('<a href="tel:{0}">{0}</a>', obj.phone)

    @admin.display(description="Age", ordering="created_at")
    def age_display(self, obj):
        delta = timezone.now() - obj.created_at
        total_minutes = int(delta.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @admin.action(description="Set status: New")
    def mark_new(self, request, queryset):
        updated = queryset.update(status=ORDER_STATUS_NEW)
        self.message_user(request, f"Updated {updated} item(s).")

    @admin.action(description="Set status: In progress")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=ORDER_STATUS_IN_PROGRESS)
        self.message_user(request, f"Updated {updated} item(s).")

    @admin.action(description="Set status: Done")
    def mark_done(self, request, queryset):
        updated = queryset.update(status=ORDER_STATUS_DONE)
        self.message_user(request, f"Updated {updated} item(s).")

    @admin.action(description="Set status: Cancelled")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=ORDER_STATUS_CANCELLED)
        self.message_user(request, f"Updated {updated} item(s).")


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
class ConditionerOrderAdmin(ConditionerOrderAdminMixin, admin.ModelAdmin):
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
        ("Meta", {"fields": ("source_page", "client_ip", "created_at", "updated_at")}),
    )
