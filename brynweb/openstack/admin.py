from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.utils.translation import ngettext

from .custom_filters import ServerLeaseStatusFilter
from .models import (
    Tenant,
    Region,
    RegionSettings,
    ServerLease,
    ServerLeaseRequest,
)


def model_str(obj):
    """Custom callable to enable use of model __str__ in list display"""
    return str(obj)


model_str.short_description = "Description"


class TenantAdmin(admin.ModelAdmin):
    list_display = ("created_tenant_name", "team", "region")
    list_filter = ("region",)
    search_fields = ("created_tenant_id", "created_tenant_name")


class ServerLeaseAdmin(admin.ModelAdmin):
    list_display = (
        "server_name",
        "team",
        "region",
        "last_renewed_at",
        "expiry",
        "user",
        "deleted",
        "shelved",
    )

    list_filter = (ServerLeaseStatusFilter,)

    search_fields = ("server_id", "server_name")

    readonly_fields = (
        "assigned_teammember",
        "server_id",
        "server_name",
        "last_renewed_at",
        "last_reminder_sent_at",
        "renewal_count",
        "tenant",
        "team",
        "region",
        "renewal_url",
        "deleted",
        "shelved",
    )

    actions = (
        "grant_indefinite_leases",
        "renew_leases",
        "shelve_servers",
        "send_renewal_reminder_emails",
    )

    def has_add_permission(self, request):
        return False

    def team(self, obj):
        return obj.tenant.team

    def user(self, obj):
        return obj.assigned_teammember.user

    def region(self, obj):
        return obj.tenant.region

    def grant_indefinite_leases(self, request, queryset):
        """
        Admin action: grant indefinite leases
        """
        updated = queryset.update(expiry=None)
        self.message_user(
            request,
            ngettext(
                f"Indefinite lease granted for '{queryset.first().server_name}'.",
                f"Indefinite leases granted for {updated} servers.",
                updated,
            ),
        )

    def shelve_servers(self, request, queryset):
        """
        Admin action: ServerLease -> Shelve Servers
        """
        # Logic and template adapted from Django source for delete action
        # https://github.com/django/django/blob/main/django/contrib/admin/actions.py
        # Note: request type is always POST, so must check for 'post' key
        opts = self.model._meta

        if request.POST.get("post"):
            # User clicked submit after confirmation
            shelved = 0
            for server_lease in queryset:
                if (
                    not (server_lease.shelved or server_lease.deleted)
                    and server_lease.has_expired
                ):
                    server_lease.shelve_server()
                    shelved += 1
            if shelved == 0:
                self.message_user(
                    request,
                    "All of the selected servers were ineligible for shelving.",
                    level=messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    ngettext(
                        f"Shelved {shelved} server.",
                        f"Shelved {shelved} servers.",
                        shelved,
                    ),
                )
            # Return None to display the change list page again.
            return None

        objects_name = ngettext("server", "servers", queryset.count())

        context = {
            **self.admin_site.each_context(request),
            "title": "Are you sure?",
            "action": "shelve_servers",
            "action_verb": "shelve",
            "objects_name": str(objects_name),
            "queryset": queryset,
            "opts": opts,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": self.media,
        }

        # Render confirmation page
        return TemplateResponse(request, "admin/confirm_action.html", context)

    def send_renewal_reminder_emails(self, request, queryset):
        """
        Admin action: Send renewal reminder emails
        """
        updated = 0
        for server_lease in queryset:
            if server_lease.expiry:
                server_lease.send_email_renewal_reminder()
                updated += 1
        self.message_user(
            request,
            ngettext(
                f"Server lease reminder emails sent for '{queryset.first().server_name}'.",
                f"Server lease reminder emails sent for {updated} servers.",
                updated,
            ),
        )

    def renew_leases(self, request, queryset):
        """
        Admin action: Renew server leases
        """
        updated = 0
        for server_lease in queryset:
            server_lease.renew_lease()
            updated += 1
        self.message_user(
            request,
            ngettext(
                f"Server lease renewed fpr '{queryset.first().server_name}'.",
                f"Server leases renewed for {updated} servers.",
                updated,
            ),
        )


class ServerLeaseRequestAdmin(admin.ModelAdmin):
    list_display = (
        model_str,
        "user",
        "closed",
        "granted",
        "created_at",
        "responded_at",
        "actioned_by",
    )

    list_filter = (
        "closed",
        "granted",
    )

    readonly_fields = (
        "user",
        "server_lease",
        "created_at",
        "granted",
        "responded_at",
        "actioned_by",
    )

    ordering = ("closed", "-created_at")

    actions = ("grant_indefinite_lease_requests", "reject_indefinite_lease_requests")

    def grant_indefinite_lease_requests(self, request, queryset):
        for lease_request in queryset:
            lease_request.grant(request)
        self.message_user(
            request, f"Indefinite leases granted for {queryset.count()} server(s)"
        )

    def reject_indefinite_lease_requests(self, request, queryset):
        for lease_request in queryset:
            lease_request.reject(request)
        self.message_user(
            request, f"Indefinite leases rejected for {queryset.count()} server(s)"
        )


class RegionSettingsInline(admin.StackedInline):
    model = RegionSettings


class RegionAdmin(admin.ModelAdmin):
    inlines = (RegionSettingsInline,)


admin.site.register(Tenant, TenantAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(ServerLease, ServerLeaseAdmin)
admin.site.register(ServerLeaseRequest, ServerLeaseRequestAdmin)
