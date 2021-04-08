from django.contrib.admin import SimpleListFilter


class ServerLeaseStatusFilter(SimpleListFilter):
    """
    Django admin filter by Server Leases status
    """

    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("active_with_expiry", "Active with Expiry"),
            ("active_overdue", "Active Overdue"),
            ("active_due", "Active Due"),
            ("active_indefinite", "Active Indefinie"),
            ("inactive", "Inactive"),
            ("deleted", "Deleted"),
            ("shelved", "Shelved"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.active()

        if self.value() == "active_with_expiry":
            return queryset.active_with_expiry()

        if self.value() == "active_overdue":
            return queryset.active_overdue()

        if self.value() == "active_due":
            return queryset.active_due()

        if self.value() == "active_indefinite":
            return queryset.active_indefinite()

        if self.value() == "inactive":
            return queryset.inactive()

        if self.value() == "deleted":
            return queryset.deleted()

        if self.value() == "shelved":
            return queryset.shelved()
