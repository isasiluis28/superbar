from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from facturas.models import FacturaCompra, FacturaVenta, FacturaVentaMercaderia, Mercaderia, Gasto, \
    FacturaCompraGasto, Recibo, Reposicion, ReposicionMercaderia, FacturaAnulada, FacturaAnuladaMercaderia
from daterange_filter.filter import DateRangeFilter
from facturas.forms import FacturaVentaForm, ReciboInlineFormSet, FacturaventaMercaderiaFormSet, \
    FacturacompraGastoFormSet, FacturaCompraForm, ReposicionForm

from django.contrib.admin.views.main import ChangeList
from django.db.models import Avg, Sum


# Register your models here.
class ReposicionMercaderiaInline(admin.TabularInline):
    model = ReposicionMercaderia
    extra = 1


class ReposicionAdmin(AjaxSelectAdmin):
    form = ReposicionForm
    list_display = ('fecha_reposicion', 'cliente', 'monto',)
    list_filter = ('delivery',)
    inlines = [ReposicionMercaderiaInline, ]


admin.site.register(Reposicion, ReposicionAdmin)


class MercaderiaInline(admin.TabularInline):
    model = FacturaVentaMercaderia
    formset = FacturaventaMercaderiaFormSet
    extra = 1


class MercaderiaInlineReadOnly(admin.TabularInline):
    model = FacturaVentaMercaderia
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
        ))
        result.remove('id')
        return result


class GastoInline(admin.TabularInline):
    model = FacturaCompraGasto
    formset = FacturacompraGastoFormSet
    extra = 2


class GastoInlineReadOnly(admin.TabularInline):
    model = FacturaCompraGasto
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
        ))
        result.remove('id')
        return result


# class FacturaCompraChangeList(ChangeList):
#
#     def get_results(self, *args, **kwargs):
#         super(FacturaCompraChangeList, self).get_results(*args, **kwargs)
#         q = self.result_list.aggregate(monto_sum=Sum('monto'))
#         # self.fac_compra = 1
#         self.monto_count = q['monto_sum']


class FacturaCompraAdmin(AjaxSelectAdmin):
    form = FacturaCompraForm
    list_display = ('fecha_factura', 'nro_factura', 'proveedor',)
    # total_functions = {'monto': sum}
    change_list_template = 'admin/facturas/changelist_admin.html'
    search_fields = ('nro_factura', 'proveedor__nombres_apellidos',)
    ordering = ('-fecha_factura',)
    list_filter = (
        ('fecha_factura', DateRangeFilter),
    )
    """
    def total_parcial(self, obj):
        total_parcial = 0
        for a in obj.facturacompragasto_set.all():
            total_parcial += a.precio_unitario
        return total_parcial

    total_parcial.short_name = 'Monto'
    """


    # list_per_page = 20

    # def get_changelist(self, request, **kwargs):
    #     return FacturaCompraChangeList

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = ('fecha_factura', 'nro_factura', 'proveedor',)
        self.readonly_fields = ()
        self.inlines = [GastoInline, ]
        return super(FacturaCompraAdmin, self).add_view(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not request.user.is_superuser:
            self.fields = ('fecha_factura', 'nro_factura', 'proveedor', 'monto',)
            self.readonly_fields = ('fecha_factura', 'nro_factura', 'proveedor', 'monto',)
            self.inlines = [GastoInlineReadOnly, ]
        return super(FacturaCompraAdmin, self).change_view(request, object_id)


admin.site.register(FacturaCompra, FacturaCompraAdmin)


class ReciboInline(admin.TabularInline):
    model = Recibo
    formset = ReciboInlineFormSet
    extra = 1


class ReciboInlineReadOnly(admin.TabularInline):
    model = Recibo
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
        ))
        result.remove('id')
        return result


# class FacturaVentaChangeList(ChangeList):
#
#     def get_results(self, *args, **kwargs):
#         super(FacturaVentaChangeList, self).get_results(*args, **kwargs)
#         q = self.result_list.aggregate(monto_sum=Sum('monto_total'),
#                                        cantidad_sum=Sum('total_vendido'),
#                                        saldo_sum=Sum('saldo'))
#         # self.fac_venta = 1
#         self.monto_count = q['monto_sum']
#         self.cantidad_count = q['cantidad_sum']
#         self.saldo_count = q['saldo_sum']


class FacturaVentaAdmin(AjaxSelectAdmin):
    form = FacturaVentaForm
    list_display = ('fecha_factura', 'nro_factura', 'cliente', 'total_vendido', 'monto_total', 'saldo', 'cancelado',)
    total_functions = {'total_vendido': sum, 'monto_total': sum, 'saldo': sum}
    change_list_template = 'admin/facturas/changelist_admin.html'
    search_fields = ('nro_factura', 'cliente__nombre', 'cliente__ruc')
    ordering = ('-fecha_factura', '-nro_factura',)
    list_filter = (
        ('fecha_factura', DateRangeFilter),
        'tipo_factura',
        'cancelado',
        'cliente__vendedor',
    )

    list_per_page = 200

    # def get_changelist(self, request, **kwargs):
    #     return FacturaVentaChangeList

    # totalsum_list = ('total_vendido', 'monto_total', 'saldo',)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['mostrar_botones'] = True
        self.inlines = [MercaderiaInline]
        self.fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'delivery',)
        self.readonly_fields = ()
        return super(FacturaVentaAdmin, self).add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        facventa = FacturaVenta.objects.get(id=object_id)
        extra_context = extra_context or {}
        extra_context['mostrar_botones'] = True
        if not request.user.is_superuser:
            if facventa.tipo_factura is 2:
                # si se trata de una factura a credito
                extra_context['mostrar_botones'] = True
                if facventa.cancelado is False:
                    # si la factura aun no fue cancelada

                    self.fields = (
                        'fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'delivery',)
                    self.readonly_fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'delivery',)
                    self.inlines = [ReciboInline, MercaderiaInlineReadOnly, ]
                else:
                    # si la factura ya fue cancelada
                    extra_context = extra_context or {}
                    extra_context['mostrar_botones'] = False
                    self.fields = (
                        'fecha_factura', 'nro_factura', 'tipo_factura', 'cancelado', 'fecha_cancelacion', 'cliente',
                        'delivery',)
                    self.readonly_fields = (
                        'fecha_factura', 'nro_factura', 'tipo_factura', 'cancelado', 'fecha_cancelacion', 'cliente',
                        'delivery',)
                    self.inlines = [ReciboInlineReadOnly, MercaderiaInlineReadOnly]
            else:
                # si se trata de una factura contado
                extra_context = extra_context or {}
                extra_context['mostrar_botones'] = False
                self.fields = (
                    'fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'delivery',)
                self.inlines = [MercaderiaInlineReadOnly, ]
                self.readonly_fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'delivery',)

        return super(FacturaVentaAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(FacturaVenta, FacturaVentaAdmin)

admin.site.register(Mercaderia)
admin.site.register(Gasto)


class MercaderiaAnuladaInline(admin.TabularInline):
    model = FacturaAnuladaMercaderia
    extra = 1

class MercaderiaAnuladaInlineReadOnly(admin.TabularInline):
    model = FacturaAnuladaMercaderia
    can_delete = False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        result = list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
        ))
        result.remove('id')
        return result


class FacturaAnuladaAdmin(AjaxSelectAdmin):
    list_display = ('fecha_factura', 'nro_factura', 'cliente', 'total_vendido', 'monto_total', )
    inlines = [MercaderiaAnuladaInline, ]
    search_fields = ('nro_factura', 'cliente__nombre',)
    ordering = ('-fecha_factura', '-nro_factura',)
    list_filter = (
        ('fecha_factura', DateRangeFilter),
        'tipo_factura',
    )

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['mostrar_botones'] = True
        self.inlines = [MercaderiaAnuladaInline]
        self.fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'vendedor',)
        self.readonly_fields = ()
        return super(FacturaAnuladaAdmin, self).add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['mostrar_botones'] = True
        if not request.user.is_superuser:
           # extra_context = extra_context or {}
            extra_context['mostrar_botones'] = False
            self.fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'vendedor', )
            self.readonly_fields = ('fecha_factura', 'nro_factura', 'tipo_factura', 'cliente', 'vendedor', )
            self.inlines = [MercaderiaAnuladaInlineReadOnly, ]
        return super(FacturaAnuladaAdmin, self).change_view(request, object_id, extra_context=extra_context)

    list_per_page = 200

admin.site.register(FacturaAnulada, FacturaAnuladaAdmin)
