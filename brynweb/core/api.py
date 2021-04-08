from django.urls import path

from . import api_views as core_views
from home import api_views as home_views
from openstack import api_views as openstack_views
from userdb import api_views as userdb_views

app_name = "api"

# Note: serial/int internal keys are not exposed externally, to avoid exposing implementation details
# & possible attack surfaces.
# Hashids are used for these objects (although these purely obfuscate, they are no substitute for properly
# secured endpoints)
# Models using uuid as primary keys are exposed directly, since these offer the same benefits.

urlpatterns = [
    # {% url "api:announcements" %}
    path(
        "announcements/",
        home_views.AnnouncementListView.as_view(),
        name="announcements",
    ),
    # {% url "api:faqs" %}
    path("faqs/", home_views.FrequentlyAskedQuestionListView.as_view(), name="faqs",),
    # {% url "api:hypervisor-stats" %}
    path(
        "hypervisor-stats/",
        openstack_views.HypervisorStatsListView.as_view(),
        name="hypervisor_stats",
    ),
    # {% url "api:keypairs" %}
    path("keypairs/", openstack_views.KeyPairListView.as_view(), name="key_pairs"),
    # {% url "api:keypairs" pk=keypair.id %}
    path(
        "keypairs/<uuid:pk>",
        openstack_views.KeyPairDetailView.as_view(),
        name="key_pairs",
    ),
    # {%url "api:messages" % }
    path("messages/", core_views.MessagesListView.as_view(), name="messages"),
    # {% url "api:tenants" team_id=team.id %}
    path(
        "teams/<hashids:team_id>/tenants/",
        openstack_views.TenantListView.as_view(),
        name="tenants",
    ),
    # {% url "api:instances" team_id=team.id tenant_id=tenant.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/instances/",
        openstack_views.InstanceListView.as_view(),
        name="instances",
    ),
    # {% url "api:instances" team_id=team.id tenant_id=tenant.id pk=instance.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/instances/<str:pk>",
        openstack_views.InstanceDetailView.as_view(),
        name="instances",
    ),
    # {% url "api:lease_requests" team_id=team.id tenant_id=tenant.id instance_id=instance.id  %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/instances/<str:instance_id>/lease-requests/",
        openstack_views.ServerLeaseRequestCreateView.as_view(),
        name="lease_requests",
    ),
    # {% url "api:flavors" team_id=team.id tenant_id=tenant.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/flavors/",
        openstack_views.FlavorListView.as_view(),
        name="flavors",
    ),
    # {% url "api:images" team_id=team.id tenant_id=tenant.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/images/",
        openstack_views.ImageListView.as_view(),
        name="images",
    ),
    # {% url "api:volumes" team_id=team.id tenant_id=tenant.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/volumes/",
        openstack_views.VolumeListView.as_view(),
        name="volumes",
    ),
    # {% url "api:volumes" team_id=team.id tenant_id=tenant.id pk=volume.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/volumes/<str:pk>",
        openstack_views.VolumeDetailView.as_view(),
        name="volumes",
    ),
    # {% url "api:volume_types" team_id=team.id tenant_id=tenant.id %}
    path(
        "teams/<hashids:team_id>/tenants/<hashids:tenant_id>/volumetypes/",
        openstack_views.VolumeTypeListView.as_view(),
        name="volume_types",
    ),
    # {% url "api:team" team_id=team.id %}
    path(
        "teams/<hashids:team_id>", userdb_views.TeamDetailView.as_view(), name="teams",
    ),
    # {% url "api:invitations" team_id=team.id %}
    path(
        "teams/<hashids:team_id>/invitations/",
        userdb_views.InvitationListView.as_view(),
        name="invitations",
    ),
    # {% url "api:invitations" team_id=team.id pk=invitation.pk %}
    path(
        "teams/<hashids:team_id>/invitations/<uuid:pk>",
        userdb_views.InvitationDetailView.as_view(),
        name="invitations",
    ),
    # {% url "api:licence-acceptances" team_id=team.id %}
    path(
        "teams/<hashids:team_id>/licence-acceptances/",
        userdb_views.LicenceAcceptanceListView.as_view(),
        name="licence_acceptances",
    ),
    # {% url "api:team_members" team_id=team.id %}
    path(
        "teams/<hashids:team_id>/members/",
        userdb_views.TeamMemberListView.as_view(),
        name="team_members",
    ),
    # {% url "api:team_members" team_id=team.id pk=teammember.id %}
    path(
        "teams/<hashids:team_id>/members/<hashids:pk>",
        userdb_views.TeamMemberDetailView.as_view(),
        name="team_members",
    ),
    # {% url "api:userprofile" %}
    path(
        "userprofile/", userdb_views.OwnUserDetailView.as_view(), name="user_profile",
    ),
]
