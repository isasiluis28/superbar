import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'superbar.settings')
django.setup()

from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ConnectionDoesNotExist
from facturas import models
from clientes.models import Cliente, Proveedor, Vendedor
from django.utils import timezone
import datetime


def setup_cursor():
    try:
        cursor = connections['legacy'].cursor()
    except ConnectionDoesNotExist:
        print "Legacy database is not configured"
        return None
    else:
        return cursor


def import_mercaderias():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, nombre FROM facturas_mercaderia"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        mercaderia = models.Mercaderia(id=row[0], nombre=row[1])
        mercaderia.save()


def import_gastos():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, concepto FROM facturas_gasto"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        gasto = models.Gasto(id=row[0], concepto=row[1])
        gasto.save()


def import_facturaventas():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """
            SELECT id, nro_factura, fecha_factura, tipo_factura, total_vendido, monto_total, fecha_creacion,
            saldo, cancelado, fecha_cancelacion, cliente_id, delivery_id FROM facturas_facturaventa
          """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            cliente = Cliente.objects.get(id=row[10])
            delivery = Vendedor.objects.get(id=row[11])
        except ObjectDoesNotExist:
            print "cliente not found with id %s" % row[8]
            continue
        else:
            # facturaventa = models.FacturaVenta(id=row[0], nro_factura=row[1], fecha_factura=row[2],
            #                                    tipo_factura=row[3], total_vendido=row[4], monto_total=row[5],
            #                                    fecha_creacion=row[6], saldo=row[7],
            #                                    cancelado=row[8], fecha_cancelacion=row[9], cliente=cliente,
            #                                    delivery=delivery)
            facturaventa = models.FacturaVenta(id=row[0],
                                               nro_factura=row[1],
                                               fecha_factura=row[2],
                                               tipo_factura=row[3],
                                               fecha_creacion=row[6],
                                               cliente=cliente,
                                               delivery=delivery)
            facturaventa.save()


def import_facturaventamercaderia():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """
            SELECT id, cantidad, precio_unitario, facturaventa_id, mercaderia_id FROM facturas_facturaventamercaderia
          """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            facturaventa = models.FacturaVenta.objects.get(id=row[3])
            mercaderia = models.Mercaderia.objects.get(id=row[4])
        except ObjectDoesNotExist:
            print "facturaventa or mercaderia not found with id's %s, %s respectively" % (row[2], row[3])
            continue
        else:
            facturaventamercaderia = models.FacturaVentaMercaderia(id=row[0], cantidad=row[1], precio_unitario=row[2],
                                                                   facturaventa=facturaventa, mercaderia=mercaderia)
            facturaventamercaderia.save()


def import_recibos():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, fecha_recibo, nro_recibo, monto, facturaventa_id FROM facturas_recibo"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            facturaventa = models.FacturaVenta.objects.get(id=row[4])
        except ObjectDoesNotExist:
            print "recibo not found with id %s" % row[4]
            continue
        else:
            recibo = models.Recibo(id=row[0], fecha_recibo=row[1], nro_recibo=row[2], monto=row[3], facturaventa=facturaventa)
            recibo.save()


def import_facturacompra():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """
            SELECT id, nro_factura, fecha_factura, fecha_creacion, monto, proveedor_id FROM facturas_facturacompra
          """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            proveedor = Proveedor.objects.get(id=row[5])
        except ObjectDoesNotExist:
            print "proveedor not found with id %s" % row[5]
            continue
        else:
            facturacompra = models.FacturaCompra(id=row[0], nro_factura=row[1],
                                                 fecha_factura=row[2],
                                                 fecha_creacion=row[3], proveedor=proveedor)
            facturacompra.save()


def import_facturacompragasto():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """
            SELECT id, cantidad, obs, precio_unitario, facturacompra_id, gasto_id FROM facturas_facturacompragasto
          """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            facturacompra = models.FacturaCompra.objects.get(id=row[4])
            gasto = models.Gasto.objects.get(id=row[5])
        except ObjectDoesNotExist:
            print "facturacompra or gasto not found with id's %s, %s respectively" % (row[4], row[5])
            continue
        else:
            facturacompragasto = models.FacturaCompraGasto(id=row[0], cantidad=row[1], obs=row[2],
                                                           precio_unitario=row[3], facturacompra=facturacompra,
                                                           gasto=gasto)
            facturacompragasto.save()


def main():
    # pass
    import_mercaderias()
    import_gastos()
    import_facturaventas()
    import_facturaventamercaderia()
    import_recibos()
    import_facturacompra()
    import_facturacompragasto()


if __name__ == "__main__":
    main()
