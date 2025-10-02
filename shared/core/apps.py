from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shared.core"
    verbose_name = "Shared Core"

    def ready(self) -> None:
        # Import signal modules or other setup hooks if needed later.
        return super().ready()
