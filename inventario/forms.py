from django import forms
from django.forms.models import BaseInlineFormSet

from inventario.models import BandejaEnProduccion
from models import Insumo, Lote, FacturaCompraProduccion, InsumoTamano, Produccion
from ajax_select.fields import AutoCompleteSelectField


class ProduccionBandejaForm(forms.ModelForm):
    class Meta:
        model = BandejaEnProduccion
        fields = ('bandeja', 'nro_lote', 'cant_bandejas', 'cant_perdida',)

    def clean(self):
        cleaned_data = super(ProduccionBandejaForm, self).clean()
        bandeja = cleaned_data.get('bandeja')
        cant_bandejas = cleaned_data.get('cant_bandejas')

        insumos_cortos = []
        for bandejainsumo in bandeja.bandejainsumo_set.all():
            total_a_utilizar = bandejainsumo.cantidad * cant_bandejas
            insumo = bandejainsumo.insumo
            stock = insumo.stock
            if total_a_utilizar > stock:
                insumos_cortos.append(insumo)
        if insumos_cortos:
            text = ''
            for insumo in insumos_cortos:
                text = text + insumo.nombre + ' / '
            raise forms.ValidationError('Insumos con stock en falta: ' + text)


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


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ('nombre', 'perecedero',)


class InsumoTamanoForm(forms.ModelForm):
    class Meta:
        model = InsumoTamano
        fields = ('insumo', 'tamano', 'cantidad',)

    def clean_cantidad(self):
        tamano = self.cleaned_data['tamano']
        cantidad = self.cleaned_data['cantidad']

        if cantidad > 0:
            if tamano is 4 and cantidad != 1:
                if cantidad is None:
                    cantidad = 1
                elif cantidad is not 1:
                    raise forms.ValidationError('Tamano Unitario: Debe tratarse con cantidad puesta en 1')
                    # cantidad = 1
        else:
            raise forms.ValidationError('La cantidad debe ser mayor a cero.')

        return cantidad


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ('insumo_tamano', 'nro_lote', 'fecha_vto', 'cant_cajas', 'costo',)

    def clean_fecha_vto(self):
        fecha_vto = self.cleaned_data.get('fecha_vto', None)
        insumo_tamano = self.cleaned_data['insumo_tamano']
        insumo = insumo_tamano.insumo
        if insumo.perecedero and fecha_vto is None:
            raise forms.ValidationError('Debe dar una fecha de vencimiento, se trata de un insumo perecedero.')
        elif insumo.perecedero is False and fecha_vto:
            fecha_vto = None
            raise forms.ValidationError('Verifique nuevamente, el insumo es no perecedero.')
        return fecha_vto


class FacturaCompraProduccionForm(forms.ModelForm):
    class Meta:
        model = FacturaCompraProduccion
        fields = ('nro_factura', 'fecha_factura', 'proveedor',)


class ProduccionForm(forms.ModelForm):
    class Meta:
        model = Produccion
        fields = ('fecha',)
