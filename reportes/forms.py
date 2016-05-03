from django import forms
from clientes.models import Vendedor


class ReporteVendedorForm(forms.Form):
    vendedor = forms.ModelChoiceField(Vendedor.objects.all())
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()

class ReporteForm(forms.Form):
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()