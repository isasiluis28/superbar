from __future__ import unicode_literals

from django.apps import AppConfig


class InventarioConfig(AppConfig):
    name = 'inventario'
    verbose_name = 'gestion de inventario'

    def ready(self):
        import inventario.signals
