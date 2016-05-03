from django import forms
from clientes.models import Cliente, Vendedor
from ajax_select.fields import AutoCompleteSelectField


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    barrio = AutoCompleteSelectField('barrios-lookup',
                                     required=False,
                                     show_help_text=False,
                                     help_text='despliega los barrios correspondientes a una cierta ciudad.')
    segmento = AutoCompleteSelectField('segmentos-lookup',
                                       required=False,
                                       show_help_text=False,
                                       help_text='Indica un tipo de cliente. Ej: Gimnasio, Particular, etc.')
    # vendedor = forms.ModelChoiceField(queryset=Vendedor.objects.all(), required=True)


class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ('usuario', 'margen_venta', 'margen_delivery')

    def clean_margen_venta(self):
        margen = self.cleaned_data['margen_venta']
        if margen is not None:
            if margen <= 0 or margen > 100:
                raise forms.ValidationError('El margen debe ser mayor a cero y menor o igual a 100')
        return self.cleaned_data['margen_venta']

    def clean_margen_delivery(self):
        margen = self.cleaned_data['margen_delivery']

        if margen is not None:
            if margen <= 0 or margen > 100:
                raise forms.ValidationError('El margen debe ser mayor a cero y menor o igual a 100')
        return self.cleaned_data['margen_delivery']
