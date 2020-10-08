from django.urls import reverse_lazy, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "user"

urlpatterns = [
    url(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="userdb/login.html",),
        name="login",
    ),
    url(r"^logout/$", auth_views.logout_then_login, name="logout"),
    url(
        r"^password_reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="userdb/password_reset_form.html",
            email_template_name="userdb/email/password_reset_email.txt",
            html_email_template_name="userdb/email/password_reset_email.html",
            subject_template_name="userdb/email/password_reset_subject.txt",
            success_url=reverse_lazy("user:password_reset_done"),
        ),
        name="password_reset",
    ),
    url(
        r"^password_reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="userdb/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    url(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="userdb/password_reset_confirm.html",
            success_url=reverse_lazy("user:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    url(
        r"^reset/done/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="userdb/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    url(r"^register/$", views.register, name="register"),
    url(r"^invite/$", views.invite, name="invite"),
    url(r"^accept-invite/(?P<uuid>[^/]+)$", views.accept_invite, name="accept-invite"),
    url(
        r"^validate-email/(?P<uuid>[^/]+)$", views.validate_email, name="validate-email"
    ),
    url(
        r"^institutions/typeahead/$",
        views.institution_typeahead,
        name="institution_typeahead",
    ),
    path(
        "api/teams/<int:team_id>/members/<int:pk>",
        views.TeamMemberDetailView.as_view(),
        name="api-teammembers-detail",
    ),
    path(
        "api/teams/<int:team_id>/members/",
        views.TeamMemberListView.as_view(),
        name="api-teammembers-list",
    ),
    path(
        "api/teams/<int:team_id>/invitations/",
        views.InvitationListView.as_view(),
        name="api-invitation-list",
    ),
]
