from django.urls import path

from . import views

app_name = "openstack"

urlpatterns = [
    path(
        "serverleases/<str:server_id>/renew/<hashids:renewal_count>",
        views.server_lease_renewal_view,
        name="server_lease_renewal",
    ),
]
