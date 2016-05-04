from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save


@receiver(post_delete, sender='inventario.Lote')
def postdelete_Lote(sender, instance, **kwargs):
    # stock_actual = instance.insumo_tamano.insumo.stock
    instance.insumo_tamano.insumo.stock -= instance.cant_total
    instance.insumo_tamano.insumo.save()


# @receiver(post_save, sender='inventario.ProduccionBandeja')
# def postsave_produccionbandeja(sender, instance, **kwargs):
#
#     for bandejainsumo in instance.bandeja.bandejainsumo_set.all():
#         saldo = bandejainsumo.cantidad * instance.cant_bandejas  # cant usada en prod
#         lotes_insumo = \
#             Lote.objects.filter(insumo_tamano__insumo=bandejainsumo.insumo, empty=False).order_by('fecha_vto')
#
#         loteenprod = LoteEnProduccion.objects.create(produccionbandeja=instance, insumo=bandejainsumo.insumo)
#         for lote in lotes_insumo:
#             if lote.saldo <= saldo:
#                 LotesInsumo.objects.create(loteenproduccion=loteenprod, lote=lote, cantidad=lote.saldo)
#                 # LoteEnProduccion.objects.create(produccionbandeja=instance, insumo=bandejainsumo.insumo,
#                 #                                 lote=lote, cantidad=lote.saldo)
#                 lote.empty = True
#                 saldo -= lote.saldo
#                 lote.saldo = 0
#                 lote.save()
#
#             else:
#                 LotesInsumo.objects.create(loteenproduccion=loteenprod, lote=lote, cantidad=saldo)
#                 # LoteEnProduccion.objects.create(produccionbandeja=instance, insumo=bandejainsumo.insumo,
#                 #                                 lote=lote, cantidad=saldo)
#                 lote.saldo -= saldo
#                 lote.save()
#                 break
