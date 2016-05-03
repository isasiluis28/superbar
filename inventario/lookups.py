from ajax_select import register, LookupChannel
from models import InsumoTamano

@register('insumotamanos-lookup')
class InsumoTamanosLookup(LookupChannel):
    model = InsumoTamano

    def get_query(self, q, request):
        return self.model.objects.filter(insumo__nombre__icontains=q).order_by('insumo__nombre')[:50]

    def format_item_display(self, item):
        return u"<span class='tag'>%s, %s (de %s)</span>" % (item.insumo, item.get_tamano_display(), item.cantidad)
