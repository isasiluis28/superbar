# -*- encoding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime, timedelta

import clientes
from facturas.models import FacturaVenta, FacturaCompra

# para reportes
from reportes.forms import ReporteVendedorForm, ReporteForm
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4, LEGAL, letter
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors


# Create your views here.


def reporte1(request):
    if request.method == 'POST':
        formulario = ReporteVendedorForm(request.POST)
        if formulario.is_valid():
            vendedor = formulario.cleaned_data['vendedor']
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            return reporte_vendedor(vendedor, fecha_inicio, fecha_fin)
    else:
        formulario = ReporteVendedorForm()
    return render_to_response('reportes/reporteVendedor.html', {'formulario': formulario},
                              context_instance=RequestContext(request))


def reporte2(request):
    if request.method == 'POST':
        formulario = ReporteForm(request.POST)
        if formulario.is_valid():
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            return reporte_ventas(fecha_inicio, fecha_fin)
    else:
        formulario = ReporteForm()
    return render_to_response('reportes/reporte.html', {'formulario': formulario},
                              context_instance=RequestContext(request))


def reporte3(request):
    if request.method == 'POST':
        formulario = ReporteForm(request.POST)
        if formulario.is_valid():
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            return reporte_compras(fecha_inicio, fecha_fin)
    else:
        formulario = ReporteForm()
    return render_to_response('reportes/reporte.html', {'formulario': formulario},
                              context_instance=RequestContext(request))


def reporte4(request):
    if request.method == 'POST':
        formulario = ReporteVendedorForm(request.POST)
        if formulario.is_valid():
            vendedor = formulario.cleaned_data['vendedor']
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            return reporte_clientes_por_cobrar(vendedor, fecha_inicio, fecha_fin)
    else:
        formulario = ReporteVendedorForm()
    return render_to_response('reportes/reporteVendedor.html', {'formulario': formulario},
                              context_instance=RequestContext(request))

def reporte5(request):
    if request.method == 'POST':
        formulario = ReporteForm(request.POST)
        if formulario.is_valid():
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']
            return reporte_general(fecha_inicio, fecha_fin)
    else:
        formulario = ReporteForm()
    return render_to_response('reportes/reporte.html', {'formulario': formulario},
                              context_instance=RequestContext(request))

def dibujar_tabla(c, data, high):
    width, height = letter  # ancho y alto de la hoja
    table = Table(data, colWidths=[2.3 * cm, 1.8 * cm, 4.4 * cm, 2 * cm, 2 * cm, 1.8 * cm, 2 * cm, 2.1 * cm, 1.3 * cm])
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (-4, -1), 'CENTER'),
        # ('TEXTCOLOR',(-3,1),(-1,-1),colors.red),
    ]))
    # pdf size
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, high)


def add_nro_pag(c, hoja_actual, total_hojas):
    c.setFont('Helvetica', 10)
    pag = "Página %s de %s" % (hoja_actual, total_hojas)
    c.drawString(95 * mm, 10 * mm, pag)


def formato_nro(numero):
    contador = int(1)
    control = int(10)
    formateado = ""
    potencia = 1
    while control <= numero:
        contador = contador + 1
        control = control * 10

    nro = str(numero)
    d = 1
    while contador > 0:
        formateado += nro[contador - 1]
        if (d % (3 * potencia)) == 0:
            formateado += "."
        contador -= 1
        d += 1
    a = ""
    contador = len(formateado)
    if formateado[len(formateado) - 1] == ".":
        contador -= 1
    while contador > 0:
        a += formateado[contador - 1]
        contador -= 1
    return a


def mostrar_totales(c, high, suma_monto, suma_comision, bandera):
    c.setFont('Times-Bold', 11)
    c.drawString(365, high - 20, "Total Monto:")
    c.drawString(440, high - 20, formato_nro(suma_monto))
    if bandera:
        c.drawString(415, high - 40, "Total Comisión:")
        c.drawString(500, high - 40, formato_nro(suma_comision))


def reporte_ventas(fecha_inicio, fecha_fin):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Reporte_Ventas.pdf"'  # borrar attachment;
    # Create the PDF object, using the BytesIO object as its "file."
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, )

    # Header
    c.setFont('Times-Bold', 18)
    c.drawString(230, 750, 'Informe de Ventas')
    # c.drawImage("superbar.png", 440, 670, width=100, height=100)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(30, 710, 'Fecha:')
    #    c.drawString(30, 700, 'Vendedor:')
    c.drawString(30, 680, 'Periodo:')
    c.setFont('Helvetica', 11)
    actual = datetime.now()
    c.drawString(80, 710, actual.strftime('%Y-%m-%d'))
    #    c.drawString(100, 700, vendedor.__str__())
    periodo = fecha_inicio.__str__() + " a " + fecha_fin.__str__()
    c.drawString(100, 680, periodo)
    # usuario = request.user
    # c.drawString(280, 720, usuario)
    # Formato para la Cabecera de la tabla
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    fecha = Paragraph('''Fecha''', styleBH)
    nro_factura = Paragraph('''Nro de Factura''', styleBH)
    cliente = Paragraph('''Cliente''', styleBH)
    tipo_fac = Paragraph('''Tipo Factura''', styleBH)
    concepto = Paragraph('''Concepto''', styleBH)
    precio_unit = Paragraph('''Precio Unitario''', styleBH)
    monto = Paragraph('''Monto''', styleBH)
    vendedor = Paragraph('''Vendedor''', styleBH)
    data = []
    data.append([fecha, nro_factura, cliente, tipo_fac, concepto, precio_unit, monto, vendedor])

    high = 600  # variable para saber donde escribir en la tabla =600

    #fecha_fin = fecha_fin + timedelta(days=1)  # le sumamos un dia para que realize bien el filtro
    facturas = FacturaVenta.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day)).order_by('fecha_factura')

    total = facturas.count()
    total_hojas = 1
    aux = total
    if total <= 28:
        total_hojas = 1
    else:
        aux -= 28
        while aux > 0:
            total_hojas += 1
            aux -= 35

    x = 0
    suma_monto = 0
    suma_comision = 0
    precio = 0
    hoja_actual = 0
    for f in facturas:
        x += 1
        concep = ""
        if f.tipo_factura == 1:
            tipo = "Contado"
        else:
            tipo = "Credito"
        for a in f.facturaventamercaderia_set.all():
            precio = a.precio_unitario
            if a.mercaderia.nombre == "SuperBar Cacao":
                concep += a.cantidad.__str__() + "C "
            elif a.mercaderia.nombre == "SuperBar Vainilla":
                concep += a.cantidad.__str__() + "V "
            else:
                concep += a.cantidad.__str__() + "F "
        this_student = [f.fecha_factura.strftime('%Y-%m-%d'), f.nro_factura[8:11], f.cliente.nombre[:22], tipo, concep,
                        formato_nro(precio),
                        formato_nro(f.monto_total), f.cliente.vendedor]
        data.append(this_student)
        suma_monto += f.monto_total
        suma_comision += f.monto_total * 0.18
        if x < 28 and x == total:
            dibujar_tabla(c, data, high)
            mostrar_totales(c, high, suma_monto, suma_comision, 0)
            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
        elif x == 28:
            dibujar_tabla(c, data, high)
            if x == total:
                mostrar_totales(c, high, suma_monto, suma_comision, 0)

            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
        elif (x % 63) == 0:
            dibujar_tabla(c, data, high)
            if x == total:
                mostrar_totales(c, high, suma_monto, suma_comision, 0)
            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
            x -= 35
            total -= 35

        high -= 18

    if data:
        dibujar_tabla(c, data, high)
        mostrar_totales(c, high, suma_monto, suma_comision, 0)
        hoja_actual += 1
        add_nro_pag(c, hoja_actual, total_hojas)
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def reporte_vendedor(vendedor, fecha_inicio, fecha_fin):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Reporte_Vendedor.pdf"'  # borrar attachment;
    # Create the PDF object, using the BytesIO object as its "file."
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, )

    # Header
    c.setFont('Times-Bold', 18)
    c.drawString(230, 750, 'Informe de Ventas')
    # c.drawImage("superbar.png", 440, 670, width=100, height=100)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(30, 720, 'Fecha:')
    # c.drawString(200, 720, 'Creado por:')
    c.drawString(30, 700, 'Vendedor:')
    c.drawString(30, 680, 'Periodo:')

    c.setFont('Helvetica-Bold', 12)
    c.drawString(330, 720, 'Referencias')
    c.drawString(320, 700, 'V & E:')
    c.drawString(330, 685, 'E:')
    c.drawString(330, 670, 'C:')
    c.setFont('Helvetica', 11)
    actual = datetime.now()
    c.drawString(80, 720, actual.strftime('%Y-%m-%d'))
    c.drawString(100, 700, vendedor.__str__())
    periodo = fecha_inicio.__str__() + " a " + fecha_fin.__str__()
    c.drawString(100, 680, periodo)
    c.drawString(365, 700, 'Venta & Entrega')
    c.drawString(365, 685, 'Entrega')
    c.drawString(365, 670, 'Cliente cedido')

    # usuario = request.user
    # c.drawString(280, 720, usuario)
    # Formato para la Cabecera de la tabla
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    fecha = Paragraph('''Fecha''', styleBH)
    nro_factura = Paragraph('''Nro de Factura''', styleBH)
    cliente = Paragraph('''Cliente''', styleBH)
    tipo_fac = Paragraph('''Tipo Factura''', styleBH)
    concepto = Paragraph('''Concepto''', styleBH)
    precio_unit = Paragraph('''Precio Unitario''', styleBH)
    monto = Paragraph('''Monto''', styleBH)
    comision = Paragraph('''Comisión''', styleBH)
    data = []
    data.append([fecha, nro_factura, cliente, tipo_fac, concepto, precio_unit, monto, comision])

    high = 600  # variable para saber donde escribir en la tabla =600

    #fecha_fin = fecha_fin + timedelta(days=1)  # le sumamos un dia para que realize bien el filtro
    facturas = FacturaVenta.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day),
            delivery__usuario__username=vendedor).order_by('fecha_factura', 'nro_factura')
    # cliente__vendedor=vendedor,
    total = facturas.count()
    total_hojas = 1
    aux = total
    if total <= 28:
        total_hojas = 1
    else:
        aux -= 28
        while aux > 0:
            total_hojas += 1
            aux -= 35

    x = 0
    suma_monto = 0
    suma_comision = 0
    precio = 0
    hoja_actual = 0
    comision_calculada = 0
    vend_str = vendedor.__str__()
    descripcion = ""
    for f in facturas:
        x += 1
        concep = ""
        if f.tipo_factura == 1:
            tipo = "Contado"
        else:
            tipo = "Credito"
        for a in f.facturaventamercaderia_set.all():
            precio = a.precio_unitario
            if a.mercaderia.nombre == "SuperBar Cacao":
                concep += a.cantidad.__str__() + "C "
            elif a.mercaderia.nombre == "SuperBar Vainilla":
                concep += a.cantidad.__str__() + "V "
            else:
                concep += a.cantidad.__str__() + "F "

        # comisiones
        if f.cliente.vendedor.usuario.username == "pachi" and f.delivery.usuario.username == "pachi":
            comision_calculada = int(f.monto_total * 0.18)
            descripcion = "V & E"
        elif f.cliente.vendedor.usuario.username == "superbar" and f.delivery.usuario.username == "pachi":
            nom = f.cliente.nombre
            if nom == "Rafael FCE ECO":
                comision_calculada = int(f.monto_total * 0.10)
                descripcion = "C"
            else:
                comision_calculada = int(f.monto_total * 0.15)
                descripcion = "E"
        elif f.cliente.vendedor.usuario.username == "alejandro" and f.delivery.usuario.username == "alejandro":
            nom = f.cliente.nombre
            if nom == "Nimia Miranda" or nom == "Julio Meza" or nom == "Gabriela Ratti" or nom == "Cavi Esculies" or nom == "Liliana Dominguez" or nom == "M & M":
                comision_calculada = int(f.monto_total * 0.10)
                descripcion = "C"
            else:
                comision_calculada = int(f.monto_total * 0.17)
                descripcion = "V & E"
        elif f.cliente.vendedor.usuario.username == "superbar" and f.delivery.usuario.username == "alejandro":
            comision_calculada = int(f.monto_total * 0.14)
            descripcion = "E"
            # print f.cliente.nombre

        if f.cliente.vendedor.usuario.username == "superbar" and f.delivery.usuario.username == "superbar":
            comision_calculada = int(f.monto_total * 0.18)
            descripcion = "V & E"
        elif f.cliente.vendedor.usuario.username != "superbar" and f.delivery.usuario.username == "superbar":
            comision_calculada = int(f.monto_total * 0.15)
            descripcion = "E"
        this_student = [f.fecha_factura.strftime('%Y-%m-%d'), f.nro_factura[8:11], f.cliente.nombre[:22], tipo, concep,
                        formato_nro(precio), formato_nro(f.monto_total), formato_nro(comision_calculada), descripcion]
        data.append(this_student)
        suma_monto += f.monto_total
        suma_comision += comision_calculada
        if x < 28 and x == total:
            dibujar_tabla(c, data, high)
            mostrar_totales(c, high, suma_monto, suma_comision, 1)
            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
        elif x == 28:
            dibujar_tabla(c, data, high)
            if x == total:
                mostrar_totales(c, high, suma_monto, suma_comision, 1)

            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
        elif (x % 63) == 0:
            dibujar_tabla(c, data, high)
            if x == total:
                mostrar_totales(c, high, suma_monto, suma_comision, 1)
            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)
            c.showPage()
            data = []
            high = 740
            x -= 35
            total -= 35

        high -= 18
    if data:
        dibujar_tabla(c, data, high)
        mostrar_totales(c, high, suma_monto, suma_comision, 1)
        hoja_actual += 1
        add_nro_pag(c, hoja_actual, total_hojas)
        c.showPage()
    # hasta acá funca bien
    if vend_str == "pachi":
        c.setFont('Times-Bold', 16)
        c.drawString(180, 740, 'Comisión por ventas de Alejandro ')
        c.setFont('Helvetica-Bold', 13)
        c.drawString(30, 700, 'Fecha:')
        c.drawString(30, 680, 'Periodo:')
        c.setFont('Helvetica', 11)
        c.drawString(80, 700, actual.strftime('%Y-%m-%d'))
        c.drawString(100, 680, periodo)
        high = 600
        para_tabla_extra = []
        para_tabla_extra.append([fecha, nro_factura, cliente, tipo_fac, concepto, precio_unit, monto, comision])
        facturas = FacturaVenta.objects.filter(
                fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
                fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day),
                delivery__usuario__username="alejandro").order_by('fecha_factura', 'nro_factura')

        total = facturas.count()
        total_hojas = 1
        aux = total
        if total <= 28:
            total_hojas = 1
        else:
            aux -= 28
            while aux > 0:
                total_hojas += 1
                aux -= 35

        x = 0
        suma_monto2 = 0
        suma_comision = 0
        precio = 0
        hoja_actual = 0
        comision_calculada = 0
        descripcion = ""
        for f in facturas:
            x += 1
            concep = ""
            if f.tipo_factura == 1:
                tipo = "Contado"
            else:
                tipo = "Credito"
            for a in f.facturaventamercaderia_set.all():
                precio = a.precio_unitario
                if a.mercaderia.nombre == "SuperBar Cacao":
                    concep += a.cantidad.__str__() + "C "
                elif a.mercaderia.nombre == "SuperBar Vainilla":
                    concep += a.cantidad.__str__() + "V "
                else:
                    concep += a.cantidad.__str__() + "F "

            # comisiones


            if f.cliente.vendedor.usuario.username == "alejandro" and f.delivery.usuario.username == "alejandro":
                nom = f.cliente.nombre
                if nom == "Nimia Miranda" or nom == "Julio Meza" or nom == "Gabriela Ratti" or nom == "Cavi Esculies" or nom == "Liliana Dominguez":
                    comision_calculada = int(f.monto_total * 0)
                else:
                    comision_calculada = int(f.monto_total * 0.01)
            elif f.cliente.vendedor.usuario.username == "superbar" and f.delivery.usuario.username == "alejandro":
                comision_calculada = int(f.monto_total * 0.01)

            this_student = [f.fecha_factura.strftime('%Y-%m-%d'), f.nro_factura[8:11], f.cliente.nombre[:22], tipo,
                            concep,
                            formato_nro(precio), formato_nro(f.monto_total), formato_nro(comision_calculada)]
            para_tabla_extra.append(this_student)
            suma_monto2 += f.monto_total
            suma_comision += comision_calculada
            if x < 28 and x == total:
                dibujar_tabla(c, para_tabla_extra, high)
                mostrar_totales(c, high, suma_monto2, suma_comision, 1)
                hoja_actual += 1
                add_nro_pag(c, hoja_actual, total_hojas)
                c.showPage()
                para_tabla_extra = []
                high = 740
            elif x == 28:
                dibujar_tabla(c, para_tabla_extra, high)
                if x == total:
                    mostrar_totales(c, high, suma_monto2, suma_comision, 1)

                hoja_actual += 1
                add_nro_pag(c, hoja_actual, total_hojas)
                c.showPage()
                para_tabla_extra = []
                high = 740
            elif (x % 63) == 0:
                dibujar_tabla(c, para_tabla_extra, high)
                if x == total:
                    mostrar_totales(c, high, suma_monto2, suma_comision, 1)
                hoja_actual += 1
                add_nro_pag(c, hoja_actual, total_hojas)
                c.showPage()
                para_tabla_extra = []
                high = 740
                x -= 35
                total -= 35

            high -= 18
        if para_tabla_extra:
            dibujar_tabla(c, para_tabla_extra, high)
            mostrar_totales(c, high, suma_monto2, suma_comision, 1)
            hoja_actual += 1
            add_nro_pag(c, hoja_actual, total_hojas)

            # c.drawString(340, high - 50, "Comisión a cobrar:")
            # c.drawString(440, high - 50, formato_nro(suma_monto+suma_monto2))

    # sigue normal
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


class PageNumCanvas(canvas.Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    # ----------------------------------------------------------------------
    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    # ----------------------------------------------------------------------
    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    # ----------------------------------------------------------------------
    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "Página %s de %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(115 * mm, 10 * mm, page)


# ----------------------------------------------------------------------


def myFirstPage(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFont('Times-Bold', 18)
    canvas.drawString(230, 750, titulo)
    # canvas.drawImage("superbar.png", 440, 670, width=100, height=100)
    canvas.setFont('Helvetica-Bold', 13)
    canvas.drawString(30, 710, 'Fecha:')
    canvas.drawString(30, 680, 'Periodo:')
    canvas.setFont('Helvetica', 11)
    actual = datetime.now()
    canvas.drawString(80, 710, actual.strftime('%Y-%m-%d'))
    periodo = f_ini.__str__() + " a " + f_fin.__str__()
    canvas.drawString(100, 680, periodo)
    canvas.restoreState()


def myFirstPage2(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFont('Times-Bold', 18)
    canvas.drawString(230, 750, titulo)
    # canvas.drawImage("superbar.png", 440, 670, width=100, height=100)
    canvas.setFont('Helvetica-Bold', 13)
    canvas.drawString(30, 720, 'Fecha:')
    canvas.drawString(30, 700, 'Vendedor:')
    canvas.drawString(30, 680, 'Periodo:')
    canvas.setFont('Helvetica', 11)
    actual = datetime.now()
    canvas.drawString(80, 720, actual.strftime('%Y-%m-%d'))
    periodo = f_ini.__str__() + " a " + f_fin.__str__()
    canvas.drawString(100, 700, vendedor_global)
    canvas.drawString(100, 680, periodo)
    canvas.restoreState()


def laterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 12)
    canvas.drawString(35, 750, "SuperBar")
    canvas.drawString(450, 750, titulo)
    actual = datetime.now()
    canvas.drawString(470, 735, actual.strftime('%Y-%m-%d'))
    canvas.restoreState()


def reporte_compras(fecha_inicio, fecha_fin):
    global f_ini
    global f_fin
    global titulo
    titulo = "Informe de Compras"
    f_ini = fecha_inicio
    f_fin = fecha_fin
    fecha_hoy = datetime.now()
    nombre_documento = "Reporte_Compras_" + fecha_hoy.strftime('%Y-%m-%d') + ".pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % nombre_documento  # borrar attachment;
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1.5 * cm, righttMargin=1 * cm)

    story = [Spacer(1, 1 * inch)]

    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    fecha = Paragraph('''Fecha''', styleBH)
    nro_factura = Paragraph('''Nro de Factura''', styleBH)
    proveedor = Paragraph('''Proveedor''', styleBH)
    concepto = Paragraph('''Concepto''', styleBH)
    precio_unit = Paragraph('''Precio Unitario''', styleBH)
    monto = Paragraph('''Monto''', styleBH)
    data = []
    data.append([fecha, nro_factura, proveedor, concepto, precio_unit, monto])
    facturas = FacturaCompra.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day)).order_by('fecha_factura')

    suma_monto = 0

    for f in facturas:
        concep = ""
        precio = ""
        total_parcial = 0
        for a in f.facturacompragasto_set.all():
            texto = a.gasto.concepto
            if a.gasto.concepto.__sizeof__() < 30:
                concep += texto + "\n"
            else:
                concep += texto[:25] + "\n"
            precio += formato_nro(a.precio_unitario) + "\n"
            total_parcial += a.precio_unitario * a.cantidad
        aux_datos = [f.fecha_factura.strftime('%Y-%m-%d'), f.nro_factura, f.proveedor.nombre, concep, precio,
                     formato_nro(total_parcial)]
        data.append(aux_datos)
        # suma_monto += f.monto
        suma_monto += total_parcial

    table = Table(data, colWidths=[2.3 * cm, 3.1 * cm, 4.1 * cm, 4.8 * cm, 1.8 * cm, 2 * cm])  # ,spaceBefore=10*inch)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
    ]))
    total = 'Monto Total: %s' % formato_nro(suma_monto)
    estilo = ParagraphStyle("pera",
                            leading=10,
                            firstLineIndent=370,
                            spacebefore=0,
                            spaceafter=0,
                            fontSize=11,
                            fontName='Times-Bold',
                            textColor=colors.black)

    p = Paragraph(total, estilo)

    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(p)

    doc.build(story, onFirstPage=myFirstPage, onLaterPages=laterPages, canvasmaker=PageNumCanvas)
    response.write(buffer.getvalue())
    buffer.close()
    return response


# para pruebas
def reporte_clientes_por_cobrar(vendedor, fecha_inicio, fecha_fin):
    global f_ini
    global f_fin
    global titulo
    global vendedor_global
    vendedor_global = vendedor.__str__()
    titulo = "Clientes por Cobrar"
    f_ini = fecha_inicio
    f_fin = fecha_fin
    fecha_hoy = datetime.now()
    nombre_documento = "ReporteClientesPorCobrar_" + fecha_hoy.strftime('%Y-%m-%d') + ".pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % nombre_documento  # borrar attachment;
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1.5 * cm, righttMargin=1 * cm)

    story = [Spacer(1, 1 * inch)]

    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 10

    fecha = Paragraph('''Fecha''', styleBH)
    nro_factura = Paragraph('''Nro de Factura''', styleBH)
    cliente = Paragraph('''Cliente''', styleBH)
    ruc = Paragraph('''Ruc''', styleBH)
    concepto = Paragraph('''Concepto''', styleBH)
    monto = Paragraph('''Monto''', styleBH)
    saldo = Paragraph('''Saldo''', styleBH)

    data = []
    data.append([ cliente,ruc,fecha, nro_factura, concepto, monto, saldo])

    #fecha_fin = fecha_fin + timedelta(days=1)  # le sumamos un dia para que realize bien el filtro
    facturas = FacturaVenta.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day),
            cliente__vendedor=vendedor).exclude(saldo=0).order_by('cliente','-fecha_factura')

    suma_monto = 0

    cliente_anterior = ""

    for f in facturas:
        concep = ""
        saldo = ""
        monto_aux = ""
        fecha_aux = ""
        nro_fact_aux = ""
        cliente_actual = f.cliente.nombre
        factura_filtrada = facturas.filter(cliente__nombre=f.cliente.nombre).order_by('fecha_factura')
        print factura_filtrada
        if cliente_actual != cliente_anterior:
            for nf in factura_filtrada:
                saldo += formato_nro(nf.saldo) + "\n"
                monto_aux += formato_nro(nf.monto_total) + "\n"
                fecha_aux += nf.fecha_factura.strftime('%Y-%m-%d') + "\n"
                nro_fact_aux += nf.nro_factura.__str__() + "\n"
                for a in nf.facturaventamercaderia_set.all():
                    if a.mercaderia.nombre == "SuperBar Cacao":
                        concep += a.cantidad.__str__() + "C "
                    elif a.mercaderia.nombre == "SuperBar Vainilla":
                        concep += a.cantidad.__str__() + "V "
                    else:
                        concep += a.cantidad.__str__() + "F "

                concep = concep + "\n"
                suma_monto += nf.saldo
            cliente_anterior = f.cliente.nombre
            aux_datos = [f.cliente.nombre[:25], f.cliente.ruc, fecha_aux, nro_fact_aux, concep, monto_aux, saldo]
            data.append(aux_datos)



    table = Table(data, colWidths=[4.7 * cm, 2.4 * cm, 2.3 * cm, 2.4 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm])  # ,spaceBefore=10*inch)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
    ]))
    total = 'Total a cobrar: %s' % formato_nro(suma_monto)
    estilo = ParagraphStyle("pera",
                            leading=10,
                            firstLineIndent=365,
                            spacebefore=0,
                            spaceafter=0,
                            fontSize=11,
                            fontName='Times-Bold',
                            textColor=colors.black)

    p = Paragraph(total, estilo)

    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(p)

    doc.build(story, onFirstPage=myFirstPage2, onLaterPages=laterPages, canvasmaker=PageNumCanvas)
    response.write(buffer.getvalue())
    buffer.close()
    return response


def reporte_general(fecha_inicio, fecha_fin):
    # Create the HttpResponse object with the appropriate PDF headers.
    fecha_hoy = datetime.now()
    nombre_documento = "ReporteGeneral_" + fecha_hoy.strftime('%Y-%m-%d') + ".pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % nombre_documento  # borrar attachment;
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, )

    # Header
    c.setFont('Times-Bold', 18)
    c.drawString(230, 750, 'Informe General')
    # c.drawImage("superbar.png", 440, 670, width=100, height=100)
    c.setFont('Helvetica', 12)
    c.drawString(500, 760, "SuperBar")
    c.setFont('Helvetica-Bold', 13)
    c.drawString(30, 710, 'Fecha:')
    c.drawString(30, 680, 'Periodo:')
    c.setFont('Helvetica', 11)
    actual = datetime.now()
    c.drawString(80, 710, actual.strftime('%Y-%m-%d'))
    periodo = fecha_inicio.__str__() + " a " + fecha_fin.__str__()
    c.drawString(95, 680, periodo)
    c.line(30,670,580,670)

    # Calculos
    #Factura Venta
    #fecha_fin = fecha_fin + timedelta(days=1)  # le sumamos un dia para que realize bien el filtro
    facturas = FacturaVenta.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day)).order_by('fecha_factura')
    cant_cacao = 0
    cant_vainilla = 0
    cant_frutilla = 0
    monto_contado = 0
    monto_credito = 0
    credito_por_cobrar = 0
    for f in facturas:

        concep = ""
        if f.tipo_factura == 1:
            tipo = "Contado"
            monto_contado += f.monto_total

        else:
            tipo = "Credito"
            monto_credito += f.monto_total
            credito_por_cobrar += f.saldo
        for a in f.facturaventamercaderia_set.all():
            precio = a.precio_unitario
            if a.mercaderia.nombre == "SuperBar Cacao":
                cant_cacao += a.cantidad
            elif a.mercaderia.nombre == "SuperBar Vainilla":
                cant_vainilla += a.cantidad
            else:
                cant_frutilla += a.cantidad

    facturas = FacturaCompra.objects.filter(
            fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
            fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day)).order_by('fecha_factura')
    monto_fac_compra = 0
    for f in facturas:
        total_parcial = 0
        for a in f.facturacompragasto_set.all():
            total_parcial += a.precio_unitario * a.cantidad

        # monto_fac_compra += f.monto
        monto_fac_compra += total_parcial

    ###############################################
    c.setFont('Helvetica-Bold', 13)
    c.drawString(380, 590, 'Cantidades Vendidas')

    c.setFont('Times-Roman', 11)
    c.drawString(350, 570, '- SuperBar Sabor Cacao:    '+cant_cacao.__str__())
    c.drawString(350, 550, '- SuperBar Sabor Vainilla: '+cant_vainilla.__str__())
    c.drawString(350, 530, '- SuperBar Sabor Frutilla:  '+cant_frutilla.__str__())

    c.setFont('Helvetica-Bold', 13)
    c.drawString(70, 590, 'Montos de Facturas')

    c.setFont('Helvetica-Bold', 10)
    c.drawString(40, 570, '- Facturas de Compra:')
    c.drawString(40, 550, '- Facturas de Venta:')
    c.drawString(70, 530, '- Contado:')
    c.drawString(70, 510, '- Crédito:')
    c.drawString(90, 490, '- Cobrado:')
    c.drawString(90, 470, '- Por cobrar:')
    c.drawString(430, 510, 'Total: ')

    c.setFont('Helvetica', 10)
    c.drawString(155, 570,  'Gs. '+formato_nro(monto_fac_compra))
    c.drawString(155, 550, 'Gs. '+formato_nro(monto_contado+monto_credito))
    c.drawString(155, 530, 'Gs. '+formato_nro(monto_contado))
    c.drawString(155, 510,'Gs. '+ formato_nro(monto_credito))
    c.drawString(155, 490, 'Gs. '+formato_nro(monto_credito-credito_por_cobrar))
    c.drawString(155, 470, 'Gs. '+formato_nro(credito_por_cobrar))
    c.drawString(460, 510,formato_nro(cant_cacao+cant_vainilla+cant_frutilla) )


    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response



# Este funciona
# def reporte_clientes_por_cobrar(vendedor, fecha_inicio, fecha_fin):
#     global f_ini
#     global f_fin
#     global titulo
#     global vendedor_global
#     vendedor_global = vendedor.__str__()
#     titulo = "Clientes por Cobrar"
#     f_ini = fecha_inicio
#     f_fin = fecha_fin
#     fecha_hoy = datetime.now()
#     nombre_documento = "Reporte_ClientesPorCobrar_" + fecha_hoy.strftime('%Y-%m-%d') + ".pdf"
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'filename=%s' % nombre_documento  # borrar attachment;
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1.5 * cm, righttMargin=1 * cm)
#     story = [Spacer(1, 1 * inch)]
#
#     styles = getSampleStyleSheet()
#     styleBH = styles["Normal"]
#     styleBH.alignment = TA_CENTER
#     styleBH.fontSize = 10
#
#     fecha = Paragraph('''Fecha''', styleBH)
#     nro_factura = Paragraph('''Nro de Factura''', styleBH)
#     cliente = Paragraph('''Cliente''', styleBH)
#     concepto = Paragraph('''Concepto''', styleBH)
#     monto = Paragraph('''Monto''', styleBH)
#     saldo = Paragraph('''Saldo''', styleBH)
#
#     data = []
#     data.append([fecha, nro_factura, cliente, concepto, monto, saldo])
#
#     facturas = FacturaVenta.objects.filter(
#             fecha_factura__gte=datetime(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day),
#             fecha_factura__lte=datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day),
#             cliente__vendedor=vendedor).exclude(saldo=0).order_by('fecha_factura')
#
#     suma_monto = 0
#
#     for f in facturas:
#         concep = ""
#
#         for a in f.facturaventamercaderia_set.all():
#             precio = a.precio_unitario
#             if a.mercaderia.nombre == "SuperBar Cacao":
#                 concep += a.cantidad.__str__() + "C "
#             elif a.mercaderia.nombre == "SuperBar Vainilla":
#                 concep += a.cantidad.__str__() + "V "
#             else:
#                 concep += a.cantidad.__str__() + "F "
#         aux_datos = [f.fecha_factura.strftime('%Y-%m-%d'), f.nro_factura, f.cliente.nombre, concep,
#                      formato_nro(f.monto_total), formato_nro(f.saldo)]
#         data.append(aux_datos)
#         suma_monto += f.saldo
#
#     table = Table(data, colWidths=[2.3 * cm, 2.6 * cm, 4.9 * cm, 2.1 * cm, 2.1 * cm])  # ,spaceBefore=10*inch)
#     table.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
#     ]))
#     total = 'Total a cobrar: %s' % formato_nro(suma_monto)
#     estilo = ParagraphStyle("pera",
#                             leading=10,
#                             firstLineIndent=350,
#                             spacebefore=0,
#                             spaceafter=0,
#                             fontSize=11,
#                             fontName='Times-Bold',
#                             textColor=colors.black)
#
#     p = Paragraph(total, estilo)
#
#     story.append(table)
#     story.append(Spacer(1, 0.2 * inch))
#     story.append(p)
#
#     doc.build(story, onFirstPage=myFirstPage2, onLaterPages=laterPages, canvasmaker=PageNumCanvas)
#     response.write(buffer.getvalue())
#     buffer.close()
#     return response

#reportes/urls
     # url(r'^informeGeneral/$', views.reporte5, name='reporte5'),

#index
        # <tr>
        #     <th><a href="/reportes/informeGeneral">Reporte General</a></th>
        #     <td></td>
        #     <td></td>
        # </tr>
