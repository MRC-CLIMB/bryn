from django.urls import path, include

from . import views

app_name = "home"

vue_urls = [
    path("", views.FrontendView.as_view(), name="home"),
    path(
        "teams/<path:vue_router_path>", views.FrontendView.as_view(), name="team_home"
    ),
]

urlpatterns = [path("", include(vue_urls))]
