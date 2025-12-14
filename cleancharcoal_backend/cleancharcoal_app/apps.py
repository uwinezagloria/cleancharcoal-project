from django.apps import AppConfig

class CleancharcoalAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cleancharcoal_app"

    def ready(self):
        from . import signals  # noqa
