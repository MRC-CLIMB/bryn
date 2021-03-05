from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect

from openstack.models import Region
from .models import (
    LicenceVersion,
    LicenceAcceptance,
    Team,
    Invitation,
    TeamMember,
    Profile,
    UserProfile,
)

from scripts.setup_team import setup_tenant


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "institution",
        "creator",
        "created_at",
        "verified",
        "tenants_available",
    )
    list_filter = ("verified",)

    actions = [
        "verify_and_send_notification_email",
        "create_warwick_tenant",
        "create_bham_tenant",
        "create_cardiff_tenant",
        "create_swansea_tenant",
    ]

    def verify_and_send_notification_email(self, request, queryset):
        n = 0
        for t in queryset:
            t.verify_and_send_notification_email()
            n += 1
        self.message_user(request, "%s teams were sent notification email" % (n,))

    def create_tenant(self, region, request, queryset):
        n = 0
        for t in queryset:
            try:
                setup_tenant(t, region)
            except Exception as e:
                self.message_user(request, "Failed to setup tenant %s: %s" % (t, e))
            n += 1
        self.message_user(request, "Created %s tenants" % (n,))

    def create_warwick_tenant(self, request, queryset):
        self.create_tenant(Region.objects.get(name="warwick"), request, queryset)

    def create_bham_tenant(self, request, queryset):
        self.create_tenant(Region.objects.get(name="bham"), request, queryset)

    def create_cardiff_tenant(self, request, queryset):
        self.create_tenant(Region.objects.get(name="cardiff"), request, queryset)

    def create_swansea_tenant(self, request, queryset):
        self.create_tenant(Region.objects.get(name="swansea"), request, queryset)

    def setup_teams(self, request, queryset):
        teams = [str(t.pk) for t in queryset]
        return HttpResponseRedirect("/setup/?ids=%s" % (",".join(teams)))


class InvitationAdmin(admin.ModelAdmin):
    list_filter = ("accepted",)

    actions = ["resend_invitation"]

    def resend_invitation(self, request, queryset):
        n = 0
        for i in queryset:
            i.send_invitation(i.made_by)
            n += 1
        self.message_user(request, "%s invitations resent" % (n,))


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    list_filter = ("profile__email_validated",)

    actions = ["resend_email_activation_link"]

    inlines = (ProfileInline,)

    def resend_email_activation_link(self, request, queryset):
        for u in queryset:
            u.profile.send_validation_link()
        self.message_user(request, "Validation links resent.")


# TODO delete legacy UserProfile admin after data transfer
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class LegacyCustomUserAdmin(UserAdmin):
    list_filter = ("userprofile__email_validated",)

    actions = ["copy_to_new_profile_table"]

    inlines = (UserProfileInline,)

    def copy_to_new_profile_table(modeladmin, request, queryset):
        for user in queryset:
            user.userprofile.copy_to_new_profile()

    def resend_email_activation_link(self, request, queryset):
        for u in queryset:
            u.profile.send_validation_link(u)
        self.message_user(request, "Validation links resent.")


def model_str(obj):
    """Custom callable to enable use of model __str__ in list display"""
    return str(obj)


model_str.short_description = "Description"


class LicenceVersionAdmin(admin.ModelAdmin):
    list_display = (
        model_str,
        "effective_date",
        "validity_period_days",
    )


admin.site.register(LicenceVersion, LicenceVersionAdmin)
admin.site.register(LicenceAcceptance)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember)
admin.site.register(Invitation, InvitationAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
