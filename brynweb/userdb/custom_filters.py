from django.contrib.admin import SimpleListFilter


class TeamLicenceFilter(SimpleListFilter):
    """
    Django admin filter by Team licence status
    """

    title = "Licence Status"
    parameter_name = "licence_status"

    def lookups(self, request, model_admin):
        return (
            ("licence_expired", "Licence Expired"),
            ("licence_valid", "Licence Valid"),
        )

    def queryset(self, request, queryset):
        if self.value() == "licence_expired":
            return queryset.licence_expired()

        if self.value() == "licence_valid":
            return queryset.licence_valid()
