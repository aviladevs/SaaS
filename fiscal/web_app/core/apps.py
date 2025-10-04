from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core - Gestão de XMLs'
    
    def ready(self):
        """Importa signals quando app está pronto"""
        import core.signals  # noqa
