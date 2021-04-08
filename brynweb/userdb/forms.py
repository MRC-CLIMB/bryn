from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from .models import Invitation, Team


class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        """
        Combined with AllowAllUsersModelBackend,
        allows for more specific login form errors
        """

        # New user, pending email activation
        if not (user.is_active or user.profile.email_validated):
            # Not active, and pending email validation
            raise forms.ValidationError(
                _(
                    "Please follow the account activation link sent to your email address."
                ),
                code="email_not_validated",
            )

        # Previously active user that has been disabled by admin
        if not user.is_active:
            raise forms.ValidationError(
                _(
                    f"This account has been disabled. Please contact {settings.ADMIN_EMAIL} for further assistance."
                ),
                code="inactive",
            )

        # No active teams
        teams = user.teams.all()
        pending_invitations = Invitation.objects.filter(
            email=user.email, accepted=False
        )
        if not (teams.verified().count() or pending_invitations.count()):
            if not len(teams):
                # No teams whatsoever
                raise forms.ValidationError(_("You have no current team memberships."))
            else:
                # No active teams
                raise forms.ValidationError(
                    _(
                        "Your team is pending approval by our admin team. We'll be in touch soon."
                    ),
                    code="no_teams",
                )


class RegistrationScreeningForm(forms.Form):
    agree_terms = forms.BooleanField(
        label="I have read and agree to the above terms and conditions", required=True
    )
    is_primary_user = forms.BooleanField(
        label="I confirm that I am the primary user for my team", required=True
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "new_password1"
        ].help_text = "Minimum 8 characters & not entirely numeric."


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        """Modify fields without redefinition"""
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields[
            "password1"
        ].help_text = "Minimum 8 characters & not entirely numeric."

    def clean_email(self):
        """
        Confirm email is unique.
        Can't enforce on a database level, since this was not set initially and several duplicates already exist.
        """
        existing = User.objects.filter(email=self.cleaned_data["email"])
        if existing.count():
            raise forms.ValidationError("A user with this email already exists.")
        else:
            return self.cleaned_data["email"]

    def save(self, commit=True):
        """Use email as username (cannot just change user model due legacy)"""
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class PrimaryUserCreationForm(CustomUserCreationForm):
    allowed_domains = ["ac.uk", "gov.uk", "nhs.uk"]

    def clean_email(self):
        """
        Confirm email is unique and part of an allowed domain.
        """
        email = self.cleaned_data["email"]

        # Check unique
        existing = User.objects.filter(email=email)
        if existing.count():
            raise forms.ValidationError("A user with this email already exists.")

        # Check domain
        domain_part = email.split("@")[-1]
        if not any(domain in domain_part for domain in self.allowed_domains):
            raise forms.ValidationError(
                f"You must use an email ending in one of: {', '.join(self.allowed_domains)}"
            )

        # Valid
        return email


class InvitedUserCreationForm(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        """Disable the email widget for invitation user creation form"""
        super().__init__(*args, **kwargs)
        self.fields["email"].disabled = True
        self.fields[
            "email"
        ].help_text = "Your registration email must match the invitation."

    agree_terms = forms.BooleanField(
        label="I have read and agree to the above terms and conditions", required=True
    )


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            "name",
            "institution",
            "department",
            "position",
            "phone_number",
            "research_interests",
            "intended_climb_use",
            "held_mrc_grants",
        )
        widgets = {
            "phone_number": PhoneNumberInternationalFallbackWidget,
        }
