from django.apps import AppConfig


class FerroVelhoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ferrovelho'
    verbose_name = 'Ferro Velho'

    def ready(self):
        import apps.ferrovelho.signals
