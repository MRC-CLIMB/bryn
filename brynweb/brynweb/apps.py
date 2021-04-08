from django.contrib.admin.apps import AdminConfig


class BrynAdminConfig(AdminConfig):
    default_site = "brynweb.admin.BrynAdminSite"
