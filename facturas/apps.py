from __future__ import unicode_literals

from django.apps import AppConfig


class FacturasConfig(AppConfig):
    name = 'facturas'
    verbose_name = 'gestion de facturas'

    def ready(self):
        import facturas.signals