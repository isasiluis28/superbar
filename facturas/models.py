from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# from datetime import datetime


# Create your models here.

class Reposicion(models.Model):
    class Meta:
        verbose_name_plural = 'Reposiciones'
        verbose_name = 'Reposicion'

    fecha_reposicion = models.DateField(default=timezone.now)
    cliente = models.ForeignKey('clientes.Cliente')
    mercaderias = models.ManyToManyField('facturas.Mercaderia', through='ReposicionMercaderia')
    delivery = models.ForeignKey('clientes.Vendedor')
    monto = models.IntegerField(default=0)  # monto total de la perdida teniendo en cuenta costo de mercaderia


class Mercaderia(models.Model):
    nombre = models.CharField(max_length=50)
    cantidad = models.IntegerField(help_text='cantidad de barritas contenidas '
                                             'en una caja', default=0)  # cantidad de barritas que entran en la caja
    costo = models.IntegerField(default=0, help_text='costo una barrita (individual)')  # costo individual

    def __unicode__(self):
        return self.nombre


# LAST CHECKPOINT
class ReposicionMercaderia(models.Model):
    reposicion = models.ForeignKey(Reposicion)
    mercaderia = models.ForeignKey(Mercaderia)

    cantidad = models.IntegerField()  # cantidad de cajas repuestas del sabor seleccionado

    def save(self, *args, **kwargs):
        self.reposicion.monto += (self.mercaderia.costo * self.mercaderia.cantidad * self.cantidad)
        self.reposicion.save()
        super(ReposicionMercaderia, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Gs. %s' % (self.mercaderia.costo * self.mercaderia.cantidad * self.cantidad)


class Gasto(models.Model):
    class Meta:
        verbose_name = 'Concepto'
        verbose_name_plural = 'Conceptos'

    concepto = models.CharField(max_length=50)

    def __unicode__(self):
        return self.concepto


class FacturaCompra(models.Model):
    class Meta:
        verbose_name = 'Factura de Compra'
        verbose_name_plural = 'Facturas de Compra'

    nro_factura = models.CharField(max_length=50, unique=True, verbose_name='Nro de Factura')
    fecha_factura = models.DateField(default=timezone.now)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    proveedor = models.ForeignKey('clientes.Proveedor')
    concepto = models.ManyToManyField(Gasto, through='FacturaCompraGasto')
    monto = models.IntegerField(default=0, verbose_name='Monto Total', blank=True)

    def __unicode__(self):
        return u'%s: %s' % (self.nro_factura, self.proveedor)

    def total_compra(self):
        suma = 0
        for gasto in self.facturacompragasto_set.all():
            suma += gasto.precio_unitario * gasto.cantidad
        self.monto = suma

    def mostrar_monto(self):
        return u'Gs. %d' % self.monto

    mostrar_monto.short_description = 'Monto Total'


class FacturaCompraGasto(models.Model):
    class Meta:
        unique_together = ('facturacompra', 'gasto',)

    facturacompra = models.ForeignKey(FacturaCompra)
    gasto = models.ForeignKey(Gasto)
    cantidad = models.IntegerField(default=0)
    obs = models.CharField(max_length=30, null=True, blank=True)
    precio_unitario = models.IntegerField(default=0, verbose_name='Precio Unitario')

    def __unicode__(self):
        return u'Total: Gs. %d' % (self.cantidad * self.precio_unitario)


class FacturaVenta(models.Model):
    class Meta:
        verbose_name = 'Factura de Venta'
        verbose_name_plural = 'Facturas de Venta'
        ordering = ['-fecha_factura', 'cliente']

    TIPO_FACTURA = (
        (1, 'Contado'),
        (2, 'Credito'),
    )

    # campos visibles
    nro_factura = models.CharField(max_length=50, unique=True, verbose_name='Nro de Factura', default='002-001-')
    fecha_factura = models.DateField(default=timezone.now)
    # fecha_factura = models.DateTimeField(default=timezone.now) anteriormente estaba asi
    cliente = models.ForeignKey('clientes.Cliente')
    tipo_factura = models.IntegerField(default=1, choices=TIPO_FACTURA)
    mercaderias = models.ManyToManyField(Mercaderia, through='FacturaVentaMercaderia')
    total_vendido = models.IntegerField(default=0)
    monto_total = models.IntegerField(default=0, verbose_name='Monto')
    delivery = models.ForeignKey('clientes.Vendedor', help_text='Vendedor que ejecuto el reparto.')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    saldo = models.IntegerField(default=0)
    cancelado = models.BooleanField(default=True)
    fecha_cancelacion = models.DateField(blank=True, null=True,
                                         help_text='la fecha en cuestion es la fecha del utlimo recibo de cancelacion.')

    def esCredito(self):
        if self.tipo_factura is 2:
            self.cancelado = False

    def __unicode__(self):
        return u'Nro. Factura: %s, Cliente: %s, Fecha: %s' % (self.nro_factura, self.cliente, self.fecha_factura)




class Recibo(models.Model):
    # class Meta:
    #     ordering = ('fecha_recibo',)
    facturaventa = models.ForeignKey(FacturaVenta)

    fecha_recibo = models.DateField(verbose_name='Fecha de recibo')
    nro_recibo = models.CharField(max_length=20)
    monto = models.IntegerField(default=0)

    def __unicode__(self):
        return self.nro_recibo


class FacturaVentaMercaderia(models.Model):
    class Meta:
        unique_together = ('facturaventa', 'mercaderia',)

    facturaventa = models.ForeignKey(FacturaVenta)
    mercaderia = models.ForeignKey(Mercaderia)

    cantidad = models.IntegerField(default=0)
    precio_unitario = models.IntegerField(default=0)

    def monto_parcial(self):
        return self.cantidad * self.precio_unitario

    def __unicode__(self):
        return u'Total: Gs. %d' % (self.cantidad * self.precio_unitario)


class FacturaAnulada(models.Model):
    class Meta:
        verbose_name = 'Factura Anulada'
        verbose_name_plural = 'Facturas Anuladas'
        ordering = ['-fecha_factura', 'cliente']

    TIPO_FACTURA = (
        (1, 'Contado'),
        (2, 'Credito'),
    )

    # campos visibles
    nro_factura = models.CharField(max_length=50, unique=True, verbose_name='Nro de Factura', default='002-001-')
    fecha_factura = models.DateField(default=timezone.now)
    cliente = models.ForeignKey('clientes.Cliente')
    tipo_factura = models.IntegerField(default=1, choices=TIPO_FACTURA)
    mercaderias = models.ManyToManyField(Mercaderia, through='FacturaAnuladaMercaderia')
    total_vendido = models.IntegerField(default=0)
    monto_total = models.IntegerField(default=0, verbose_name='Monto')
    vendedor = models.ForeignKey('clientes.Vendedor', null=True,help_text='Vendedor al cual pertenece la factura anulada.')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return u'Nro. Factura: %s, Cliente: %s, Fecha: %s' % (self.nro_factura, self.cliente, self.fecha_factura)

    def total_compra(self):
        suma = 0
        cantidad = 0
        for aux in self.facturaanuladamercaderia_set.all():
            suma += aux.precio_unitario * aux.cantidad
            cantidad += aux.cantidad
        self.monto_total = suma
        self.total_vendido = cantidad


class FacturaAnuladaMercaderia(models.Model):
    class Meta:
        unique_together = ('facturaanulada', 'mercaderia',)

    facturaanulada = models.ForeignKey(FacturaAnulada)
    mercaderia = models.ForeignKey(Mercaderia)

    cantidad = models.IntegerField(default=0)
    precio_unitario = models.IntegerField(default=0)

    def monto_parcial(self):
        return self.cantidad * self.precio_unitario

    def __unicode__(self):
        return u'Total: Gs. %d' % (self.cantidad * self.precio_unitario)
