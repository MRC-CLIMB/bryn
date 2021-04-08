from django.urls import path

from . import views

app_name = "discourse"

urlpatterns = [
    path("sso", views.sso),
]
