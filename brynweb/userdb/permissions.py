from rest_framework import permissions, exceptions

from .models import Team, TeamMember


class IsTeamMembershipAdmin(permissions.BasePermission):
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


class TeamMembershipDeleteIsNotSelf(permissions.BasePermission):
    """
    Forbid action to delete own team membership.
    """

    def has_object_permission(self, request, view, obj):
        """
        Reject if the TeamMembership user is also the request user.
        """
        if request.method != "DELETE":
            return True
        return request.user != obj.user
