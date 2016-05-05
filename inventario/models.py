from __future__ import unicode_literals

from django.utils import timezone

from django.db import models


# Create your models here.

class Insumo(models.Model):
    nombre = models.CharField(max_length=50)
    perecedero = models.BooleanField(default=False, verbose_name='Insumo perecedero',
                                     help_text='marcar si se trata de un insumo perecedero')  # nuevo
    stock = models.FloatField(default=0)  # gramos o  unidades en total que quedan de un cierto insumo

    def __unicode__(self):
        return self.nombre


class InsumoTamano(models.Model):
    class Meta:
        verbose_name = 'Tamano de Insumo'
        verbose_name_plural = 'Tamano de Insumos'
        unique_together = ('insumo', 'tamano',)

    TAMANOS = (
        (1, 'Chico'),
        (2, 'Mediano'),
        (3, 'Grande'),
        (4, 'Unitario'),
        (5, 'Inicial')
    )
    insumo = models.ForeignKey(Insumo)
    tamano = models.IntegerField(choices=TAMANOS)
    cantidad = models.FloatField()  # gramos o unidades que contiene el insumo en tal tamano

    def __unicode__(self):
        return u'%s, %s (de %s g.)' % (self.insumo, self.get_tamano_display(), self.cantidad)


class FacturaCompraProduccion(models.Model):
    class Meta:
        verbose_name = 'Factura de Compra'
        verbose_name_plural = 'Facturas de Compra'

    nro_factura = models.CharField(max_length=50, unique=True, verbose_name='Nro de Factura')
    fecha_factura = models.DateTimeField(default=timezone.now)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    proveedor = models.ForeignKey('clientes.Proveedor')
    monto = models.IntegerField(default=0)


class Lote(models.Model):
    fac_produccion = models.ForeignKey(FacturaCompraProduccion)
    fecha_creacion = models.DateTimeField(default=timezone.now)  # nuevo
    insumo_tamano = models.ForeignKey(InsumoTamano, verbose_name='Insumo')
    nro_lote = models.CharField(max_length=50, unique=True, verbose_name='Nro. de lote', help_text='lote de insumo')
    # fecha = models.DateField(default=timezone.now)
    fecha_vto = models.DateField(verbose_name='Fecha de vencimiento', blank=True, null=True, help_text='completar '
                                                                                                       'solo en caso '
                                                                                                       'de contar con '
                                                                                                       'fecha de '
                                                                                                       'vencimiento.')
    cant_cajas = models.IntegerField()  # cantidad de cajas compradas del tamano del insumo
    costo = models.IntegerField(default=0, help_text='costo unitario')
    cant_total = models.FloatField()  # gramos o unidades de todas las cajas de tal lote en gramos
    saldo = models.FloatField()  # gramos o unidades que quedan por utilizar del lote

    def save(self, *args, **kwargs):
        if self.pk is None:
            # crea nuevo Lote
            self.saldo = self.cant_total = self.insumo_tamano.cantidad * self.cant_cajas
            self.fac_produccion.monto += (self.costo * self.cant_cajas)
            self.fac_produccion.save()
            self.insumo_tamano.insumo.stock += self.cant_total
            self.insumo_tamano.insumo.save()
        # else:
        #     # si se resta del lote el saldo
        #     lote = Lote.objects.get(pk=self.pk)
        #     self.insumo_tamano.insumo.stock -= (lote.saldo - self.saldo)
        #     self.insumo_tamano.insumo.save()

        super(Lote, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s' % (self.nro_lote, self.insumo_tamano)


class Bandeja(models.Model):
    nombre = models.CharField(max_length=50)
    cantidad = models.IntegerField(help_text='cantidad de barritas en bandeja')  # cantidad de barritas por bandeja
    insumos = models.ManyToManyField(Insumo, through='BandejaInsumo')

    def __unicode__(self):
        return self.nombre


class BandejaInsumo(models.Model):
    class Meta:
        unique_together = ('bandeja', 'insumo',)

    bandeja = models.ForeignKey(Bandeja)
    insumo = models.ForeignKey(Insumo)

    cantidad = models.FloatField(help_text='gramos o unidades del insumo utilizado en una '
                                           'bandeja.')  # cantidad en gramos utilizada del insumo en la bandeja


class Produccion(models.Model):
    fecha = models.DateField(default=timezone.now)
    bandejas_usadas = models.ManyToManyField(Bandeja, through='BandejaEnProduccion')
    costo_total = models.IntegerField(default=0)


class BandejaEnProduccion(models.Model):
    produccion = models.ForeignKey(Produccion)
    bandeja = models.ForeignKey(Bandeja)
    cant_bandejas = models.IntegerField()
    costo_bandeja = models.IntegerField(default=0)
    nro_lote = models.CharField(max_length=50, help_text='lote de produccion', verbose_name='Nro. de lote', unique=True)
    cant_perdida = models.IntegerField(help_text='cantidad de barritas perdidas del tipo de bandeja', default=0,
                                       verbose_name='Cantidad Perdida')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        # ver la cantidad total de cada insumo a utilizar
        for bandejainsumo in self.bandeja.bandejainsumo_set.all():
            insumo = bandejainsumo.insumo
            cantidad_total = bandejainsumo.cantidad * self.cant_bandejas
            lote_list = Lote.objects.filter(insumo_tamano__insumo=insumo).order_by('fecha_vto').exclude(saldo=0)
            for lote in lote_list:
                if lote.saldo > cantidad_total:
                    self.costo_bandeja += cantidad_total * (lote.costo/lote.insumo_tamano.cantidad)
                    lote.saldo -= cantidad_total
                    lote.save()
                    bandejainsumo.insumo.stock -= cantidad_total
                    bandejainsumo.insumo.save()
                    break
                else:
                    self.costo_bandeja += lote.saldo * (lote.costo/lote.insumo_tamano.cantidad)
                    lote.saldo = 0
                    lote.save()
                    bandejainsumo.insumo.stock -= lote.saldo
                    bandejainsumo.insumo.save()
        self.produccion.costo_total += self.costo_bandeja
        self.produccion.save()

    class Meta:
        unique_together = ('produccion', 'bandeja')