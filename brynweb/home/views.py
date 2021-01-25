from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from humps import camelize

from openstack.models import Region
from openstack.serializers import RegionSerializer
from userdb.serializers import TeamSerializer, UserSerializer


class TeamDashboard(LoginRequiredMixin, TemplateView):
    """
    Team dashboard (home)
    """

    template_name = "home/dashboard.html"

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        user_data = camelize(UserSerializer(user).data)
        user_teams = user.teams.all()
        team_data = camelize(TeamSerializer(user_teams, many=True).data)
        region_data = camelize(RegionSerializer(Region.objects.all(), many=True).data)

        return {"regions": region_data, "teams": team_data, "user": user_data}
