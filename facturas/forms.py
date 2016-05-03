from django import forms
from django.forms.models import BaseInlineFormSet
from facturas.models import FacturaVenta, FacturaCompra, Reposicion
from ajax_select.fields import AutoCompleteSelectField


class ReposicionForm(forms.ModelForm):
    cliente = AutoCompleteSelectField('clientes-lookup',
                                      show_help_text=False,
                                      help_text='busqueda segun el nombre del cliente.',
                                      required=True
                                      )

    class Meta:
        model = Reposicion
        fields = ('fecha_reposicion', 'cliente', 'mercaderias', 'delivery')


class FacturaCompraForm(forms.ModelForm):
    proveedor = AutoCompleteSelectField('proveedores-lookup',
                                        show_help_text=False,
                                        help_text='busqueda segun el nombre del proveedor.',
                                        required=True
                                        )

    class Meta:
        model = FacturaCompra
        fields = '__all__'


# 0981 448 172
# retirar con Armando Fernandez

class FacturaventaMercaderiaFormSet(BaseInlineFormSet):
    def clean(self):
        count = 0
        super(FacturaventaMercaderiaFormSet, self).clean()

        if forms:
            for form in self.forms:
                if form.cleaned_data:
                    count += 1
                    cantidad = form.cleaned_data['cantidad']
                    precio_unitario = form.cleaned_data['precio_unitario']

                    if cantidad <= 0 or precio_unitario <= 0:
                        raise forms.ValidationError('monto y cantidad, ambos deben ser valores mayores a cero.')
        if count < 1:
            raise forms.ValidationError('Debe tener como minimo una Mercaderia.')


class FacturacompraGastoFormSet(BaseInlineFormSet):
    def clean(self):
        count = 0
        super(FacturacompraGastoFormSet, self).clean()

        if forms:
            for form in self.forms:
                if form.cleaned_data:
                    count += 1
                    cantidad = form.cleaned_data['cantidad']
                    precio_unitario = form.cleaned_data['precio_unitario']

                    if cantidad <= 0 or precio_unitario <= 0:
                        raise forms.ValidationError('monto y cantidad, ambos deben ser valores mayores a cero.')
        if count < 1:
            raise forms.ValidationError('Debe tener como minimo un Gasto.')


class ReciboInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(ReciboInlineFormSet, self).clean()
        total = 0
        first = True
        facturaventa = None

        # print(self.forms)
        for form in self.forms:
            if form.cleaned_data:
                delete = form.cleaned_data.get('DELETE', False)
                if delete:
                    continue
                else:
                    if first:
                        facturaventa = form.cleaned_data['facturaventa']
                        fecha_piso = facturaventa.fecha_factura
                        first = False
                    monto = int(form.cleaned_data['monto'])
                    fecha_recibo = form.cleaned_data['fecha_recibo']
                    if fecha_recibo < fecha_piso:
                        raise forms.ValidationError('Las fechas de los recibos deben ir yendo en orden ascendente, '
                                                    'teniendo como piso a la fecha de la misma factura.')
                    if monto <= 0:
                        raise forms.ValidationError('Los montos de los recibos no pueden contener valores menores '
                                                    'o iguales a cero.')
                    total += monto
                    fecha_piso = fecha_recibo

        if facturaventa is not None:
            if total > facturaventa.monto_total:
                raise forms.ValidationError('El total de los recibos no puede ser mayor a la deuda.')


class FacturaVentaForm(forms.ModelForm):
    class Meta:
        model = FacturaVenta
        fields = '__all__'

    cliente = AutoCompleteSelectField('clientes-lookup',
                                      show_help_text=False,
                                      help_text='busqueda segun el nombre del cliente.',
                                      required=True
                                      )

    def clean_nro_factura(self):
        nro_factura = str(self.cleaned_data['nro_factura'])
        split_nrofactura = nro_factura.split('-')

        if split_nrofactura[2] == '':
            raise forms.ValidationError('Debe completar el nro de la factura 002-001-....')

        return self.cleaned_data['nro_factura']

    def clean_cancelado(self):
        tipo_factura = self.cleaned_data['tipo_factura']
        cancelado = self.cleaned_data.get('cancelado', False)

        if tipo_factura is 1 and cancelado is False:
            self.data['cancelado'] = True
            raise forms.ValidationError('No debe cambiar el valor de este campo si se trata de una factura contado')
        return self.cleaned_data['cancelado']
