from django.apps import AppConfig


class AppAccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_accounting'

    def ready(self):
        import app_accounting.signals
