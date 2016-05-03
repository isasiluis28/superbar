from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

from facturas.models import FacturaVenta, Recibo


@receiver((post_save, post_delete), sender="facturas.FacturaCompraGasto")
def actualizar_monto(sender, instance, **kwargs):
    instance.facturacompra.total_compra()
    instance.facturacompra.save()


@receiver(post_delete, sender='facturas.Recibo')
def postdelete_recibo(sender, instance, **kwargs):
    pre_save.disconnect(presave_factventa, sender=FacturaVenta)
    # post_save.disconnect(postsave_facventa, sender=FacturaVenta)

    instance.facturaventa.saldo += instance.monto
    instance.facturaventa.save()

    pre_save.connect(presave_factventa, sender=FacturaVenta)
    # post_save.connect(postsave_facventa, sender=FacturaVenta)


@receiver(pre_save, sender='facturas.Recibo')
def presave_recibo(sender, instance, **kwargs):
    precio_distinto = False
    pre_save.disconnect(presave_factventa, sender=FacturaVenta)
    # post_save.disconnect(postsave_facventa, sender=FacturaVenta)

    # si ya existe un recibo
    if instance._state.adding is False:
        old_recibo = Recibo.objects.get(pk=instance.pk)

        if old_recibo.monto != instance.monto:
            instance.facturaventa.saldo += old_recibo.monto
            precio_distinto = True

    # si es un recibo nuevo o el monto del recibo viejo vario
    if instance._state.adding is True or precio_distinto is True:

        monto = instance.monto
        saldo = instance.facturaventa.saldo

        if monto <= saldo:
            # debitar el monto del monto del recibo
            instance.facturaventa.saldo -= monto
            if instance.facturaventa.saldo == 0:

                # si no se cambio a cancelado True, entonces setearlo a True
                # if instance.facturaventa.cancelado is False:
                #     instance.facturaventa.cancelado = True
                instance.facturaventa.cancelado = True
                instance.facturaventa.fecha_cancelacion = instance.fecha_recibo
                # si no se brindo de una fecha de cancelacion, se completa automaticamente
                # if instance.facturaventa.fecha_cancelacion is None:
                #     instance.facturaventa.fecha_cancelacion = instance.fecha_recibo
            else:
                # si todavia no llega a saldo cero, entonces ignorar fecha puesta en fecha_cancelacion
                if instance.facturaventa.fecha_cancelacion:
                    instance.facturaventa.fecha_cancelacion = None

            instance.facturaventa.save()
        else:
            raise ValidationError('El monto a debitar es mayor al saldo. Favor verifique.')

    pre_save.connect(presave_factventa, sender=FacturaVenta)
    # post_save.connect(postsave_facventa, sender=FacturaVenta)


@receiver(pre_save, sender='facturas.FacturaVenta')
def presave_factventa(sender, instance, **kwargs):
    if instance._state.adding is True:  # tambien puedo por created
        # si es una factura nueva
        if instance.tipo_factura is 2:
            instance.cancelado = False
        else:
            instance.saldo = 0


@receiver(post_save, sender='facturas.FacturaVentaMercaderia')
def postsave_facturaventamercaderia(sender, instance, **kwargs):
    cantidad = instance.cantidad
    precio_unitario = instance.precio_unitario

    # post_save.disconnect(postsave_facventa, sender=FacturaVenta)
    pre_save.disconnect(presave_factventa, sender=FacturaVenta)

    # cliente = instance.facturaventa.cliente

    # actualizo el valor del total_vendio
    instance.facturaventa.total_vendido += cantidad

    # actualizo el valor del monto_total
    instance.facturaventa.monto_total += (cantidad * precio_unitario)

    # actualizo la cantidad de cajas vendidas por el vendedor
    # vendedor = instance.facturaventa.cliente.vendedor
    # vendedor.cantidad_vendida += cantidad
    # vendedor.save()

    # verifico si es una factura credito
    if instance.facturaventa.tipo_factura is 2:
        # seteo el saldo con el valor del monto_total
        instance.facturaventa.saldo = instance.facturaventa.monto_total

    # guardo los cambios guardado
    instance.facturaventa.save()

    # creo una referencia al cliente en cuestion
    cliente = instance.facturaventa.cliente

    # verifico de que se trate de la factura con mayor fecha
    facs = FacturaVenta.objects.filter(cliente=cliente)
    last_fac = facs.latest('fecha_factura')
    if last_fac.fecha_factura == instance.facturaventa.fecha_factura:
        # actualizo los valores de ultima compra y ultima cantidad del cliente
        change_fecha_cant_cliente(cliente)

    # post_save.connect(postsave_facventa, sender=FacturaVenta)
    pre_save.connect(presave_factventa, sender=FacturaVenta)


# @receiver(post_save, sender='facturas.FacturaVenta')
# def postsave_facventa(sender, instance, **kwargs):
#     created = kwargs['created']
#     if created is True:
#         change_fecha_cant_cliente(cliente=instance.cliente)

@receiver(post_delete, sender='facturas.FacturaVenta')
def postdelete_facventa(sender, instance, **kwargs):
    change_fecha_cant_cliente(cliente=instance.cliente)

    # actualizo la cantidad de cajas vendidas por el vendedor si es que se borro una factura
    # vendedor = instance.cliente.vendedor
    # vendedor.cantidad_vendida -= instance.total_vendido
    # vendedor.save()


def change_fecha_cant_cliente(cliente):
    cant_vendida = None
    fecha = None
    facs = FacturaVenta.objects.filter(cliente=cliente)
    if facs:
        # si existen las facturas
        last_fac = facs.latest('fecha_factura')

        facs_samedate = facs.filter(fecha_factura=last_fac.fecha_factura)

        if facs_samedate:
            cant_vendida = 0
            for fac in facs_samedate:
                cant_vendida += fac.total_vendido
            fecha = last_fac.fecha_factura
    cliente.fecha_ult_compra = fecha
    cliente.last_cantidad = cant_vendida
    cliente.save()


@receiver((post_save), sender="facturas.FacturaAnuladaMercaderia")
def actualizar_monto(sender, instance, **kwargs):
    instance.facturaanulada.total_compra()
    instance.facturaanulada.save()