def get_teams_for_user(user, team=None, admin=None):
    """
    Return a queryset for all teams that an authenticated user is a member of.
    If team is specified, returns a queryset with only that team, if the user is a member.
    If team & admin are specified, returns a query set with only that team, if the user is an admin.
    """
    if team:
        if admin:
            return user.teams.filter(pk=team, team_memberships__is_admin=True)
        return user.teams.filter(pk=team)
    else:
        return user.teams.all()
