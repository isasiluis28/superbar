from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from clientes.models import Cliente, Proveedor, Ciudad, Segmento, Barrio, Vendedor
from forms import ClienteForm, VendedorForm


class BarrioInline(admin.StackedInline):
    model = Barrio
    extra = 1


class CiudadAdmin(admin.ModelAdmin):
    inlines = [BarrioInline, ]


admin.site.register(Ciudad, CiudadAdmin)


# Register your models here.
class ClienteAdmin(AjaxSelectAdmin):
    form = ClienteForm
    # fieldsets = (
    #     (None, {
    #         'fields': ('nombre', 'ruc', 'contacto', 'vendedor')
    #     }),
    #     ('Informacion Extra', {
    #         'fields': ('email', 'segmento', 'telefono', 'barrio', 'direccion',),
    #     }),
    # )
    list_display = ('nombre', 'ruc', 'segmento', 'barrio', 'fecha_ult_compra', 'last_cantidad',)
    list_filter = ('segmento', 'barrio__ciudad', 'vendedor',)
    search_fields = ('nombre', 'ruc', 'contacto')
    ordering = ('-fecha_ult_compra', 'nombre', 'barrio',)

    def save_model(self, request, obj, form, change):
        # try:
        #     vendedor = Vendedor.objects.get(usuario=request.user)
        # except Vendedor.DoesNotExist:
        #     vendedor = None
        #
        # if vendedor is None:
        if request.is_vendedor is 0:
            obj.save()
        else:
            obj.vendedor = request.vendedor
            obj.save()

    def add_view(self, request, form_url='', extra_context=None):
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
        except Vendedor.DoesNotExist:
            vendedor = None

        if vendedor is None:
            # si NO es un vendedor
            self.fieldsets = (
                (None, {
                    'fields': ('nombre', 'ruc', 'contacto', 'vendedor')
                }),
                ('Informacion Extra', {
                    'fields': ('email', 'segmento', 'telefono', 'barrio', 'direccion',),
                }),
            )
            request.is_vendedor = 0
        else:
            # si es un vendedor
            self.fieldsets = (
                (None, {
                    'fields': ('nombre', 'ruc', 'contacto')
                }),
                ('Informacion Extra', {
                    'fields': ('email', 'segmento', 'telefono', 'barrio', 'direccion',),
                }),
            )
            request.is_vendedor = 1
            request.vendedor = vendedor
            
        return super(ClienteAdmin, self).add_view(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
        except Vendedor.DoesNotExist:
            vendedor = None

        if vendedor is None:
            # si NO es un vendedor

            self.fieldsets = (
                (None, {
                    'fields': ('nombre', 'ruc', 'contacto', 'vendedor')
                }),
                ('Informacion Extra', {
                    'fields': ('email', 'segmento', 'telefono', 'barrio', 'direccion',),
                }),
            )
            # request.is_vendedor = 0
        else:
            # si es un vendedor
            self.fieldsets = (
                (None, {
                    'fields': ('nombre', 'ruc', 'contacto', 'vendedor')
                }),
                ('Informacion Extra', {
                    'fields': ('email', 'segmento', 'telefono', 'barrio', 'direccion',),
                }),
            )
            # self.readonly_fields = ('vendedor',)

            cliente = Cliente.objects.get(id=object_id)
            vendedor_real = cliente.vendedor
            if vendedor.pk == vendedor_real.pk:
                # si el vendedor logueado esta tratando de editar su cliente
                self.readonly_fields = ('vendedor',)
            else:
                # si el vendedor logueado pasa a ver clientes ajenos al mismo
                self.readonly_fields = ('nombre', 'ruc', 'contacto', 'vendedor', 'email',
                                        'segmento', 'telefono', 'barrio', 'direccion',)

        request.is_vendedor = 0

        return super(ClienteAdmin, self).change_view(request, object_id)



admin.site.register(Cliente, ClienteAdmin)

class BarrioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ciudad',)
    list_filter = ('ciudad',)


admin.site.register(Barrio, BarrioAdmin)


class VendedorAdmin(admin.ModelAdmin):
    form = VendedorForm
    list_display = ('usuario', 'margen_venta_percentage', 'margen_delivery_percentage')

    def margen_venta_percentage(self, obj):
        if obj.margen_venta is None:
            return u'No especificado'
        else:
            return u'%s %%' % obj.margen_venta

    margen_venta_percentage.short_description = 'Margen de Venta'

    def margen_delivery_percentage(self, obj):
        if obj.margen_delivery is None:
            return u'No especificado'
        else:
            return u'%s %%' % obj.margen_delivery

    margen_delivery_percentage.short_description = 'Margen de Reparto'


admin.site.register(Vendedor, VendedorAdmin)


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email')


admin.site.register(Proveedor, ProveedorAdmin)

admin.site.register(Segmento)
