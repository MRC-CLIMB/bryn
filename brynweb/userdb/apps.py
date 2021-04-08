from django.apps import AppConfig


class UserdbConfig(AppConfig):
    name = "userdb"

    def ready(self):
        # Signal registration
        import userdb.signals  # noqa
