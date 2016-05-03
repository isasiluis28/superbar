from django.apps import AppConfig


class ClientesConfig(AppConfig):
    name = 'clientes'
    verbose_name = 'gestion de terceros'

    def ready(self):
        import clientes.signals
