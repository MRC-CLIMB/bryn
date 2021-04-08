from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import exceptions, generics, permissions

from .models import Invitation, LicenceAcceptance, LicenceVersion, Team, TeamMember
from .permissions import (
    IsTeamAdminForUnsafePermission,
    IsTeamMemberPermission,
)
from .serializers import (
    InvitationSerializer,
    LicenceAcceptanceSerializer,
    TeamSerializer,
    TeamMemberSerializer,
    UserSerializer,
)
from .helpers import get_teams_for_user

User = get_user_model()


class TeamDetailView(generics.RetrieveUpdateAPIView):
    """
    API detail endpoint for Team.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]
    serializer_class = TeamSerializer
    lookup_url_kwarg = (
        "team_id"  # using team_id keeps view compatible with team permission classes
    )

    def get_queryset(self):
        return get_teams_for_user(self.request.user)


class TeamMemberListView(generics.ListAPIView):
    """
    API list endpoint for TeamMember.
    """

    serializer_class = TeamMemberSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]

    def get_queryset(self):
        team_id = self.kwargs.get("team_id")
        teams = get_teams_for_user(self.request.user, team=team_id)
        return TeamMember.objects.filter(team__in=teams)


class TeamMemberDetailView(generics.RetrieveDestroyAPIView):
    """
    API detail endpoint for TeamMember.
    """

    serializer_class = TeamMemberSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]

    def get_queryset(self):
        teams = get_teams_for_user(self.request.user)
        return TeamMember.objects.filter(team__in=teams)

    def delete(self, request, team_id, pk):
        teammember = get_object_or_404(TeamMember, pk=pk)
        if teammember.user == request.user:
            # Don't allow a team member to delete themselves
            raise exceptions.MethodNotAllowed("Own team membership cannot be deleted.")
        return super().delete(self, request, team_id, pk)


class InvitationListView(generics.ListCreateAPIView):
    """
    API list endpoint for Invitation.
    """

    serializer_class = InvitationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]

    def get_queryset(self):
        team_id = self.kwargs.get("team_id")
        teams = get_teams_for_user(self.request.user, team=team_id)
        return Invitation.objects.filter(to_team__in=teams, accepted=False)

    def perform_create(self, serializer):
        """
        Set to_team from url resolver
        """
        team = get_object_or_404(Team, pk=self.request.resolver_match.kwargs["team_id"])
        invitation = serializer.save(to_team=team)
        invitation.send_invitation_email()


class InvitationDetailView(generics.RetrieveDestroyAPIView):
    """
    API detail endpoint for Invitation.
    """

    serializer_class = InvitationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]
    queryset = Invitation.objects.all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        if self.request.method == "DELETE" and obj.accepted:
            # Don't allow accepted invitations to be deleted
            raise exceptions.MethodNotAllowed("Accepted invitations cannot be deleted.")
        return obj


class OwnUserDetailView(generics.RetrieveUpdateAPIView):
    """
    API detail endpoint for authenticated/own User.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class LicenceAcceptanceListView(generics.ListCreateAPIView):
    """
    API detail endpoint for LicenceAcceptance.
    """

    serializer_class = LicenceAcceptanceSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeamMemberPermission,
        IsTeamAdminForUnsafePermission,
    ]

    def get_queryset(self):
        team_id = self.kwargs.get("team_id")
        teams = get_teams_for_user(self.request.user, team=team_id)
        return LicenceAcceptance.objects.filter(team__in=teams)

    def perform_create(self, serializer):
        """
        Set team from url resolver, user from request
        """
        team = get_object_or_404(Team, pk=self.request.resolver_match.kwargs["team_id"])
        try:
            licence_version = LicenceVersion.objects.current()
        except LicenceVersion.DoesNotExist:
            raise exceptions.APIException(
                code=500, detail="No current Licence version exists."
            )

        serializer.save(
            licence_version=licence_version, team=team, user=self.request.user
        )
