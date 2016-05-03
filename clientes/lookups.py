from ajax_select import register, LookupChannel
from models import Cliente, Barrio, Segmento, Proveedor


@register('proveedores-lookup')
class ProveedoresLookup(LookupChannel):
    model = Proveedor

    def get_query(self, q, request):
        return self.model.objects.filter(nombre__icontains=q).order_by('nombre')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s, %s</span>" % (item.ruc, item.nombre)


@register('clientes-lookup')
class ClientesLookup(LookupChannel):
    model = Cliente

    def get_query(self, q, request):
        return self.model.objects.filter(nombre__icontains=q).order_by('nombre')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s, %s</span>" % (item.ruc, item.nombre)


@register('segmentos-lookup')
class SegmentosLookup(LookupChannel):
    model = Segmento

    def get_query(self, q, request):
        return self.model.objects.filter(nombre__icontains=q).order_by('nombre')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.nombre


@register('barrios-lookup')
class BarriosLookup(LookupChannel):
    model = Barrio

    def get_query(self, q, request):
        return self.model.objects.filter(ciudad__nombre__icontains=q).order_by('ciudad__nombre')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s, %s</span>" % (item.ciudad, item.nombre)
