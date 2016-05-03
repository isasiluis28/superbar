from django.contrib import admin
from models import Insumo, InsumoTamano, Lote, Bandeja, BandejaInsumo, Produccion, ProduccionBandeja, FacturaCompraProduccion
from forms import InsumoForm, LoteForm, FacturaCompraProduccionForm, \
    ProduccionBandejaForm, InsumoTamanoForm, ProduccionForm
from ajax_select.admin import AjaxSelectAdmin
# Register your models here.

admin.site.register(InsumoTamano)


class InsumoTamanoInline(admin.StackedInline):
    model = InsumoTamano
    form = InsumoTamanoForm
    extra = 3


class InsumoAdmin(admin.ModelAdmin):
    form = InsumoForm
    list_display = ['nombre', 'stock', 'perecedero']
    list_filter = ('perecedero',)
    inlines = [InsumoTamanoInline,]


admin.site.register(Insumo, InsumoAdmin)


class LoteInline(admin.StackedInline):
    model = Lote
    form = LoteForm
    extra = 2


class FacturaCompraProdAdmin(admin.ModelAdmin):
    form = FacturaCompraProduccionForm
    list_display = ['fecha_factura', 'nro_factura', 'proveedor', 'monto',]
    inlines = [LoteInline,]

admin.site.register(FacturaCompraProduccion, FacturaCompraProdAdmin)


class BandejaInsumoInline(admin.StackedInline):
    model = BandejaInsumo
    extra = 3


class BandejaAdmin(admin.ModelAdmin):
    inlines = [BandejaInsumoInline,]


admin.site.register(Bandeja, BandejaAdmin)


class ProduccionBandejaInline(admin.StackedInline):
    model = ProduccionBandeja
    form = ProduccionBandejaForm
    extra = 3


class ProduccionAdmin(admin.ModelAdmin):
    form = ProduccionForm
    inlines = [ProduccionBandejaInline,]


admin.site.register(Produccion, ProduccionAdmin)
