from __future__ import unicode_literals
from django.db import models
from facturas.models import FacturaVenta


# Create your models here.
# class Empleado(models.Model):
#     DEPARTAMENTOS = (
#         (1, 'Ventas'),
#         (2, 'Informatica'),
#         (3, 'Produccion'),
#     )
#     usuario = models.OneToOneField('auth.User')
#     departamento = models.IntegerField(choices=DEPARTAMENTOS)
#
#     def __unicode__(self):
#         return u'%s, %s' % (self.usuario, self.departamento)


class Vendedor(models.Model):
    class Meta:
        verbose_name_plural = 'Vendedores'
        verbose_name = 'Vendedor'

    usuario = models.OneToOneField('auth.User')
    margen_venta = models.FloatField(null=True, blank=True)
    margen_delivery = models.FloatField(null=True, blank=True)
    # cantidad_vendida = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s' % self.usuario


class Ciudad(models.Model):
    class Meta:
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

    nombre = models.CharField(max_length=50, verbose_name='Ciudad')

    def __unicode__(self):
        return self.nombre


class Barrio(models.Model):
    nombre = models.CharField(max_length=50)
    ciudad = models.ForeignKey(Ciudad)

    def __unicode__(self):
        return u'%s, %s' % (self.ciudad, self.nombre)


class Segmento(models.Model):
    class Meta:
        verbose_name = 'Segmento'
        verbose_name_plural = 'Segmentos'

    nombre = models.CharField(max_length=50)

    def __unicode__(self):
        return self.nombre


class Cliente(models.Model):
    class Meta:
        ordering = ['nombre']

    ruc = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, verbose_name='Nombre o Razon Social')
    telefono = models.CharField(max_length=50, blank=True)
    contacto = models.CharField(max_length=50, blank=True,
                                help_text='Persona con la que establecio contacto en el predio.')
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True)
    barrio = models.ForeignKey(Barrio, blank=True, null=True)
    segmento = models.ForeignKey(Segmento, help_text='Indica un tipo de cliente. Ej: Gimnasio, Particular, etc.',
                                 null=True, blank=True, verbose_name='Segmento')
    fecha_ult_compra = models.DateField(blank=True, null=True, verbose_name='Fecha de ultima venta')
    last_cantidad = models.IntegerField(blank=True, null=True, verbose_name='Ultima cantidad vendida')
    vendedor = models.ForeignKey('clientes.Vendedor', null=True, blank=True, help_text='vendedor al que'
                                                                                       'corresponde el cliente.')

    def __unicode__(self):
        return u'%s, %s' % (self.ruc, self.nombre)


class Proveedor(models.Model):
    class Meta:
        verbose_name_plural = 'Proveedores'
        verbose_name = 'Proveedor'

    nombre = models.CharField(max_length=50, verbose_name='Nombre o Razon Social')
    ruc = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    contacto = models.CharField(max_length=50, blank=True, help_text='Persona con la que establecio contacto.')
    email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return u'%s, %s' % (self.ruc, self.nombre)
