from django.contrib import messages
from django.contrib.auth import views as auth_views, get_user_model, login
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView

from .forms import (
    CustomAuthenticationForm,
    CustomSetPasswordForm,
    InvitedUserCreationForm,
    PrimaryUserCreationForm,
    RegistrationScreeningForm,
    TeamForm,
)
from .models import LicenceAcceptance, LicenceVersion, Invitation, TeamMember
from .tokens import account_activation_token

User = get_user_model()


# Auth views
class LoginView(auth_views.LoginView):
    template_name = "userdb/login.html"
    form_class = CustomAuthenticationForm


class PasswordResetView(auth_views.PasswordResetView):
    template_name = "userdb/password_reset_form.html"
    email_template_name = "userdb/email/password_reset_email.txt"
    html_email_template_name = "userdb/email/password_reset_email.html"
    subject_template_name = "userdb/email/password_reset_subject.txt"
    success_url = reverse_lazy("user:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "userdb/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "userdb/password_reset_confirm.html"
    success_url = reverse_lazy("user:password_reset_complete")
    form_class = CustomSetPasswordForm


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "userdb/password_reset_complete.html"


class RegistrationScreeningView(FormView):
    """Registration screening view"""

    template_name = "userdb/register.html"
    form_class = RegistrationScreeningForm
    success_url = reverse_lazy("user:register_team")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            licence_terms = LicenceVersion.objects.current().licence_terms
        except LicenceVersion.DoesNotExist:
            licence_terms = None
        context["licence_terms"] = licence_terms
        return context


def team_registration_view(request):
    """Team registration form view"""

    if request.method == "POST":
        user_form = PrimaryUserCreationForm(request.POST)
        team_form = TeamForm(request.POST)

        if user_form.is_valid() and team_form.is_valid():
            with transaction.atomic():
                user = user_form.save(
                    commit=False
                )  # profile instance is created via. signal
                user.is_active = False  # pending email validation
                user.save()

                # create team
                team = team_form.save(commit=False)
                team.creator = user
                team.save()

                # create team member
                member = TeamMember(team=team, user=user, is_admin=True)
                member.save()

                # create initial licence  acceptance
                licence_acceptance = LicenceAcceptance(user=user, team=team)
                licence_acceptance.save()

            return HttpResponseRedirect(reverse("user:register_team_done"))
    else:
        user_form = PrimaryUserCreationForm()
        team_form = TeamForm()

    return render(
        request,
        "userdb/register_team.html",
        {"user_form": user_form, "team_form": team_form},
    )


class TeamRegistrationDoneView(TemplateView):
    """Team registration done view"""

    template_name = "userdb/register_team_done.html"


class EmailValidationSentView(TemplateView):
    """User email validation sent view"""

    template_name = "userdb/email_validation_sent.html"


class EmailValidationConfirmView(RedirectView):
    """Mark user profile as email validated and redirect to login"""

    pattern_name = "home:home"

    def get_redirect_url(self, *args, **kwargs):
        """Check activation token"""
        try:
            user_id = urlsafe_base64_decode(kwargs.pop("uidb64"))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404

        if account_activation_token.check_token(user, kwargs.pop("token")):
            user.profile.mark_email_validated()
            messages.success(
                self.request, "Thank you for confirming your email address."
            )
        else:
            messages.error(
                self.request,
                "Account activation link has expired. We've sent you a new one!",
            )
            user.profile.send_validation_link()

        return super().get_redirect_url(*args, **kwargs)


class EmailChangeConfirmView(RedirectView):
    """Confirm email change and redirect to home"""

    pattern_name = "home:home"

    def get_redirect_url(self, *args, **kwargs):
        """Check activation token"""
        try:
            user_id = urlsafe_base64_decode(kwargs.pop("uidb64"))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404

        if account_activation_token.check_token(user, kwargs.pop("token")):
            user.profile.confirm_email_change()
            messages.success(self.request, "Your new email address has been verified.")
        else:
            messages.error(
                self.request,
                "Your email verification link has expired. We've sent you a new one!",
            )
            user.profile.send_email_change_verification(self.request)

        return super().get_redirect_url(*args, **kwargs)


@require_http_methods(["GET", "POST"])
def accept_invitation_view(request, uuid):
    """Accept invitation / user signup view"""
    # Confirm invitation is valid, and has not been accepted already
    invitation = get_object_or_404(Invitation, uuid=uuid)
    if invitation.accepted:
        messages.error(request, "This invitation has already been accepted.")
        return HttpResponseRedirect(reverse("home:home"))

    success_message = (
        f"Congratulations! You are now a member of {invitation.to_team.name}"
    )

    if request.method == "GET":
        # Handle logged in user case
        if request.user.is_authenticated:
            if request.user.email != invitation.email:
                # Email does not match
                messages.error(
                    request,
                    "You cannot accept this team invitation, because the email address does not match the one "
                    "associated with your account. Please sign in with a different account, or request a new invite.",
                )
                return HttpResponseRedirect(reverse("user:logout"))
            else:
                # Email matches
                invitation.create_team_membership(request.user)
                messages.success(request, success_message)
                return HttpResponseRedirect(reverse("home:home"))

        # Not logged in GET: initialise form
        form = InvitedUserCreationForm(initial={"email": invitation.email})

    # POST: Create User and TeamMembership, redirect to login
    if request.method == "POST":
        form = InvitedUserCreationForm(
            request.POST, initial={"email": invitation.email}
        )
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                teammember = invitation.create_team_membership(user)

                user.profile.email_validated = True  # Since they received the invite
                user.profile.default_team_membership = (
                    teammember  # Since it's their first & only team
                )
                user.save()

            messages.success(request, success_message)
            login(
                request,
                user,
                backend="django.contrib.auth.backends.AllowAllUsersModelBackend",
            )
            return HttpResponseRedirect(reverse("home:home"))

    login_url = f"{reverse('user:login')}?next={request.path}"

    try:
        licence_terms = LicenceVersion.objects.current().licence_terms
    except LicenceVersion.DoesNotExist:
        licence_terms = None

    return render(
        request,
        "userdb/accept_invitation_register.html",
        {
            "form": form,
            "licence_terms": licence_terms,
            "login_url": login_url,
            "to_team": invitation.to_team,
        },
    )


class CurrentUserLicenceView(TemplateView):
    template_name = "userdb/user_licence.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            licence_version = LicenceVersion.objects.current()
        except LicenceVersion.DoesNotExist:
            licence_version = None
        context["licence_version"] = licence_version
        return context
