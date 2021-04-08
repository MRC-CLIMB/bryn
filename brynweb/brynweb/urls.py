from django.urls import include, path, register_converter
from django.contrib import admin

from core.converters import HashidsConverter

register_converter(HashidsConverter, "hashids")

urlpatterns = [
    path("api/", include("core.api")),
    path("admin/", admin.site.urls),
    path("discourse/", include("discourse.urls")),
    path("service/", include("openstack.urls")),
    path("user/", include("userdb.urls")),
    path("", include("home.urls")),
]
