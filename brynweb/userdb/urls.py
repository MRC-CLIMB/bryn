from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "user"

urlpatterns = [
    # Auth routes
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.logout_then_login, name="logout"),
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        r"reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Registration
    path("register/", views.RegistrationScreeningView.as_view(), name="register",),
    path("register/team/", views.team_registration_view, name="register_team"),
    path(
        "register/team/done/",
        views.TeamRegistrationDoneView.as_view(),
        name="register_team_done",
    ),
    path(
        "email-validation-sent",
        views.EmailValidationSentView.as_view(),
        name="email_validation_sent",
    ),
    path(
        "accept-invitation/<uuid:uuid>/",
        views.accept_invitation_view,
        name="accept_invitation",
    ),
    path(
        "validate-email/<uidb64>/<token>/",
        views.EmailValidationConfirmView.as_view(),
        name="validate_email",
    ),
    path(
        "validate-email-change/<uidb64>/<token>/",
        views.EmailChangeConfirmView.as_view(),
        name="validate_email_change",
    ),
    path("licence/", views.CurrentUserLicenceView.as_view(), name="licence",),
]
