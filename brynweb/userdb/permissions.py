from rest_framework import permissions, exceptions

from .models import Team, TeamMember


class IsTeamAdminPermission(permissions.BasePermission):
    """
    Only allow team admins.
    """

    def has_permission(self, request, view):
        """
        Check whether the current user is admin for the team.
        """
        try:
            team_id = request.resolver_match.kwargs["team_id"]
            Team.objects.get(pk=team_id)
            team_member = TeamMember.objects.get(team=team_id, user=request.user)
        except Team.DoesNotExist:
            raise exceptions.NotFound  # No team
        except TeamMember.DoesNotExist:
            return False  # Team exists, but user is not a member
        return team_member.is_admin


class IsTeamAdminForUnsafePermission(IsTeamAdminPermission):
    """
    Only allow team admins to perform usafe methods.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsTeamMemberPermission(permissions.BasePermission):
    """
    Only allow team members.
    """

    def has_permission(self, request, view):
        """
        Check whether the current user is a member of the team.
        """
        try:
            team_id = request.resolver_match.kwargs["team_id"]
            Team.objects.get(pk=team_id)
            TeamMember.objects.get(team=team_id, user=request.user)
            return True
        except Team.DoesNotExist:
            raise exceptions.NotFound  # No team
        except TeamMember.DoesNotExist:
            return False  # Team exists, but user is not a member
