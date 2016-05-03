import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'superbar.settings')
django.setup()

from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ConnectionDoesNotExist
from clientes import models
from django.contrib.auth.models import User


def setup_cursor():
    try:
        cursor = connections['legacy'].cursor()
    except ConnectionDoesNotExist:
        print "Legacy database is not configured"
        return None
    else:
        return cursor


def import_ciudades():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, nombre FROM clientes_ciudad"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        ciudad = models.Ciudad(id=row[0], nombre=row[1])
        ciudad.save()


def import_barrios():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, nombre, ciudad_id FROM clientes_barrio"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            ciudad = models.Ciudad.objects.get(id=row[2])
        except ObjectDoesNotExist:
            print('Error')
        else:
            barrio = models.Barrio(id=row[0], nombre=row[1], ciudad=ciudad)
            barrio.save()


def import_segmentos():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, nombre FROM clientes_segmento"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        segmento = models.Segmento(id=row[0], nombre=row[1])
        segmento.save()


def import_clientes():
    cursor = setup_cursor()
    if cursor is None:
        return
    sql = """SELECT id, ruc, nombre, telefono, contacto, email, direccion, fecha_ult_compra, last_cantidad,
            barrio_id, segmento_id, vendedor_id FROM clientes_cliente"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            barrio = None
            segmento = None
            if row[9] is not None:
                barrio = models.Barrio.objects.get(id=row[9])
            if row[10] is not None:
                segmento = models.Segmento.objects.get(id=row[10])
            if row[11] is not None:
                vendedor = models.Vendedor.objects.get(id=row[11])

        except ObjectDoesNotExist:
            print "Segmento not found with id %s" % row[10]
            continue
        else:
            # cliente = models.Cliente(id=row[0], ruc=row[1], nombre=row[2], telefono=row[3], contacto=row[4],
            #                          email=row[5], direccion=row[6], fecha_ult_compra=row[7],
            #                          last_cantidad=row[8], barrio=barrio, segmento=segmento)
            cliente = models.Cliente(id=row[0], ruc=row[1], nombre=row[2], telefono=row[3], contacto=row[4],
                                     email=row[5], direccion=row[6], barrio=barrio, segmento=segmento, vendedor=vendedor)
            cliente.save()


def import_proveedores():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, nombre, ruc, direccion, telefono, contacto, email FROM clientes_proveedor"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        proveedor = models.Proveedor(id=row[0], nombre=row[1], ruc=row[2], direccion=row[3],
                                     telefono=row[4], contacto=row[5], email=row[6])
        proveedor.save()


def import_vendedores():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """SELECT id, margen_venta, margen_delivery, usuario_id FROM clientes_vendedor"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            usuario = User.objects.get(id=row[3])
        except ObjectDoesNotExist:
            print('Error')
        else:
            vendedor = models.Vendedor(id=row[0], usuario=usuario)
            vendedor.save()


def set_vendedor_to_cliente():
    cursor = setup_cursor()
    if cursor is None:
        return
    ## it's important selecting the id field, so that we can keep the publisher - book relationship
    sql = """
            SELECT cliente_id, vendedor_id FROM facturas_facturaventa
          """
    cursor.execute(sql)
    for row in cursor.fetchall():
        try:
            cliente = models.Cliente.objects.get(id=row[0])
            delivery = models.Vendedor.objects.get(id=row[1])
        except ObjectDoesNotExist:
            print('Error')
        else:
            if cliente.vendedor is None:
                cliente.vendedor = delivery
                cliente.save()


def main():
    # pass
    import_ciudades()
    import_barrios()
    import_segmentos()
    import_vendedores()
    import_clientes()
    import_proveedores()


    # set_vendedor_to_cliente()


if __name__ == "__main__":
    main()
