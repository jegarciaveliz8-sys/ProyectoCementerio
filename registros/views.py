from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import Nicho
import io
import os

def dashboard(request):
    total = Nicho.objects.count()
    ocupados = Nicho.objects.exclude(nombre_difunto__isnull=True).exclude(nombre_difunto="").count()
    disponibles = total - ocupados
    mora_count = Nicho.objects.filter(monto_arbitrio__lte=0).exclude(nombre_difunto="").count()
    recaudado = Nicho.objects.aggregate(Sum('monto_arbitrio'))['monto_arbitrio__sum'] or 0
    return render(request, 'registros/dashboard.html', {'total': total, 'ocupados': ocupados, 'disponibles': disponibles, 'mora_total': mora_count, 'recaudado': recaudado})

def mapa_cimenterio(request):
    nichos = Nicho.objects.exclude(lat__isnull=True).exclude(lng__isnull=True)
    return render(request, 'registros/mapa.html', {'nichos': nichos})

def datos_nichos_json(request):
    # --- EL RADAR DE BÚSQUEDA MEJORADO ---
    query = request.GET.get('q', '')
    if query:
        nichos = Nicho.objects.filter(
            Q(codigo__icontains=query) | 
            Q(nombre_difunto__icontains=query) | 
            Q(propietario__icontains=query)
        )
    else:
        nichos = Nicho.objects.all()
    
    data = [{'id': n.id, 'codigo': n.codigo, 'nombre_difunto': n.nombre_difunto or 'DISPONIBLE', 'propietario': n.propietario or 'S/P', 'lat': n.lat, 'lng': n.lng, 'monto_arbitrio': float(n.monto_arbitrio)} for n in nichos]
    return JsonResponse(data, safe=False)

def imprimir_ficha(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return render(request, 'registros/ficha_impresion.html', {'nicho': nicho})

def imprimir_todos_qrs(request):
    nichos = Nicho.objects.exclude(qr_code__isnull=True).exclude(qr_code='')
    return render(request, 'registros/imprimir_qrs.html', {'nichos': nichos})

def dibujar_membrete(p, width, titulo_doc):
    logo_path = os.path.join(settings.BASE_DIR, 'registros', 'static', 'img', 'logo_muni.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 50, 700, width=65, height=65, mask='auto')
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2 + 35, 740, "MUNICIPALIDAD DE SANARATE")
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2 + 35, 725, "DEPARTAMENTO DE CEMENTERIOS - GESTIÓN INTEGRAL")
    p.line(50, 695, 560, 695)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, 670, titulo_doc)

def ficha_tecnica_pro(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    dibujar_membrete(p, width, "FICHA TÉCNICA DE CAMPO")
    p.setFillColor(colors.whitesmoke); p.rect(50, 480, 510, 160, fill=1); p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12); p.drawString(70, 615, f"INFORMACIÓN DEL NICHO: {nicho.codigo}")
    y = 590
    for label, valor in [("Nombre del Difunto:", nicho.nombre_difunto or "SIN REGISTRO"), ("Propietario:", nicho.propietario or "S/P"), ("Monto Arbitrio:", f"Q{nicho.monto_arbitrio}"), ("Ubicación GPS:", f"{nicho.lat}, {nicho.lng}" if nicho.lat else "NO ASIGNADAS")]:
        p.setFont("Helvetica-Bold", 11); p.drawString(80, y, label)
        p.setFont("Helvetica", 11); p.drawString(230, y, str(valor)); y -= 25
    p.line(100, 150, 250, 150); p.drawCentredString(175, 135, "FIRMA INSPECTOR")
    p.line(350, 150, 500, 150); p.drawCentredString(425, 135, "SELLO MUNICIPAL")
    if nicho.qr_code: p.drawImage(nicho.qr_code.path, 460, 40, width=80, height=80)
    p.setFont("Helvetica-Oblique", 7); p.drawString(50, 30, f"Generado por: {request.user.username} | {timezone.now().strftime('%d/%m/%Y')}")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def generar_titulo_propiedad(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    p.setStrokeColor(colors.black); p.setLineWidth(3); p.rect(30, 30, 550, 730)
    dibujar_membrete(p, letter[0], "TÍTULO DE PROPIEDAD PERPETUA")
    p.setFont("Helvetica", 12); p.drawCentredString(300, 580, "POR EL PRESENTE SE HACE CONSTAR QUE EL DERECHO SOBRE EL NICHO PERTENECE A:")
    p.setFont("Helvetica-Bold", 16); p.drawCentredString(300, 550, f"{nicho.propietario or 'S/P'}")
    p.setFont("Helvetica-Bold", 13); p.drawCentredString(300, 500, f"UBICACIÓN: {nicho.codigo}")
    if nicho.qr_code: p.drawImage(nicho.qr_code.path, 460, 50, width=80, height=80)
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_orden_exhumacion(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    width = letter[0]
    p.setFillColor(colors.red); dibujar_membrete(p, width, "ORDEN DE EXHUMACIÓN Y TRASLADO"); p.setFillColor(colors.black)
    p.setFont("Helvetica", 11); p.drawString(50, 620, f"Se autoriza la exhumación de restos en el nicho {nicho.codigo} por motivo de vencimiento/falta de pago.")
    p.setFont("Helvetica-Bold", 11); p.drawString(50, 600, f"DIFUNTO: {nicho.nombre_difunto or 'N/A'}")
    p.rect(50, 430, 510, 140)
    p.drawString(60, 545, "DATOS DEL TRASLADO:"); p.setFont("Helvetica", 10)
    p.drawString(60, 520, "Destino de los restos: __________________________________________________")
    p.drawString(60, 490, "Familiar Responsable: __________________________________________________")
    p.drawString(60, 460, "DPI de Responsable: ___________________________________________________")
    p.line(100, 200, 250, 200); p.drawCentredString(175, 185, "ADMINISTRACIÓN")
    p.line(350, 200, 500, 200); p.drawCentredString(425, 185, "AUTORIDAD MUNICIPAL")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_traspaso_derechos(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    dibujar_membrete(p, letter[0], "ACTA DE TRASPASO DE DERECHOS")
    p.setFont("Helvetica", 11); p.drawString(50, 620, f"Yo, {nicho.propietario or 'S/P'}, propietario del nicho {nicho.codigo}, cedo mis derechos a:")
    p.drawString(50, 590, "NUEVO DUEÑO: _________________________________________________________")
    p.drawString(50, 560, "DPI: ______________________________  TELÉFONO: _________________________")
    p.line(100, 300, 250, 300); p.drawCentredString(175, 285, "FIRMA CEDENTE")
    p.line(350, 300, 500, 300); p.drawCentredString(425, 285, "FIRMA ADQUIRIENTE")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_permiso_construccion(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    dibujar_membrete(p, letter[0], "PERMISO DE CONSTRUCCIÓN Y MANTENIMIENTO")
    p.rect(50, 530, 510, 100)
    p.setFont("Helvetica-Bold", 11); p.drawString(60, 605, f"NICHO: {nicho.codigo}"); p.drawString(60, 585, f"PROPIETARIO: {nicho.propietario or 'S/P'}")
    p.setFont("Helvetica", 11); p.drawString(50, 500, "ALBAÑIL AUTORIZADO: __________________________________________________")
    p.drawString(50, 470, "TRABAJO: [ ] Lápida  [ ] Repello  [ ] Azulejo  [ ] Otros")
    p.drawCentredString(300, 150, "_________________________________")
    p.drawCentredString(300, 135, "SELLO DE VIGILANCIA CEMENTERIO")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def consulta_publica(request, codigo):
    nicho = get_object_or_404(Nicho, codigo=codigo)
    es_moroso = nicho.monto_arbitrio <= 0
    context = {'nicho': nicho, 'es_moroso': es_moroso, 'fecha_servidor': timezone.now()}
    return render(request, 'registros/consulta_inspector.html', context)

def pdf_notificacion_mora(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    width = letter[0]
    p.setFillColor(colors.darkred); dibujar_membrete(p, width, "NOTIFICACIÓN DE COBRO Y ESTADO DE MORA")
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12); p.drawString(50, 630, f"ATENCIÓN PROPIETARIO: {nicho.propietario or 'S/P'}")
    p.setFont("Helvetica", 11)
    cuerpo = [
        f"Se le informa que el nicho identificado con el código {nicho.codigo}, del cual usted es responsable,",
        f"presenta un saldo pendiente de pago. Según nuestros registros, el monto es de: Q{nicho.monto_arbitrio}.",
        "",
        "De no hacerse efectivo el pago en los próximos 30 días calendario, la municipalidad",
        "queda facultada para iniciar el proceso de exhumación y recuperación del espacio según",
        "el reglamento vigente de cementerios de Sanarate."
    ]
    y = 600
    for linea in cuerpo:
        p.drawString(50, y, linea); y -= 20
    p.rect(50, 400, 510, 80, fill=0)
    p.setFont("Helvetica-Bold", 10); p.drawCentredString(width/2, 450, "PRESENTAR ESTE AVISO EN TESORERÍA MUNICIPAL PARA SOLVENTAR")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_acta_inhumacion(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    dibujar_membrete(p, letter[0], "ACTA OFICIAL DE INHUMACIÓN")
    p.setFont("Helvetica", 11)
    p.drawString(50, 630, f"En el municipio de Sanarate, siendo la fecha {timezone.now().strftime('%d/%m/%Y')},")
    p.drawString(50, 610, f"se procede a la inhumación de los restos de: {nicho.nombre_difunto or 'N/A'}")
    p.drawString(50, 590, f"en el nicho código: {nicho.codigo}.")
    p.setFont("Helvetica-Bold", 11); p.drawString(50, 550, "DATOS DE CONTROL:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 530, "Certificado de Defunción (RENAP): _______________________________")
    p.drawString(60, 510, "Empresa Funeraria: _____________________________________________")
    p.drawString(60, 490, "Familiar que entrega: ___________________________________________")
    p.line(100, 250, 250, 250); p.drawCentredString(175, 235, "ADMINISTRADOR")
    p.line(350, 250, 500, 250); p.drawCentredString(425, 235, "RECIBÍ CONFORME (FAMILIAR)")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_solvencia_municipal(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    width = letter[0]
    dibujar_membrete(p, width, "CERTIFICACIÓN DE SOLVENCIA DE ARBITRIOS")
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 600, "EL DEPARTAMENTO DE CEMENTERIOS DE LA MUNICIPALIDAD DE SANARATE")
    p.setFont("Helvetica-Bold", 14); p.drawCentredString(width/2, 570, "CERTIFICA:")
    p.setFont("Helvetica", 12)
    texto = [
        f"Que el nicho identificado con el código {nicho.codigo},",
        f"a nombre del propietario: {nicho.propietario or 'S/P'},",
        f"SE ENCUENTRA SOLVENTE en el pago de sus arbitrios municipales",
        f"a la presente fecha: {timezone.now().strftime('%d/%m/%Y')}."
    ]
    y = 530
    for linea in texto:
        p.drawCentredString(width/2, y, linea); y -= 25
    p.setFont("Helvetica-Bold", 12); p.drawCentredString(width/2, 400, "VALIDACIÓN POR SISTEMA G.I.S.")
    if nicho.qr_code: p.drawImage(nicho.qr_code.path, width/2 - 40, 300, width=80, height=80)
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def pdf_reporte_inspeccion(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO(); p = canvas.Canvas(buffer, pagesize=letter)
    dibujar_membrete(p, letter[0], "BOLETA DE INSPECCIÓN TÉCNICA")
    p.setFont("Helvetica-Bold", 11); p.drawString(50, 630, f"ESTADO FÍSICO DEL NICHO: {nicho.codigo}")
    p.setFont("Helvetica", 10)
    items = ["ESTADO DE LA LOSA: [ ] Bueno [ ] Regular [ ] Malo", 
             "ESTADO DE PINTURA: [ ] Bueno [ ] Regular [ ] Malo",
             "DAÑOS ESTRUCTURALES: __________________________________________",
             "OBSERVACIONES: ________________________________________________",
             "______________________________________________________________"]
    y = 600
    for item in items:
        p.drawString(60, y, item); y -= 30
    p.rect(50, 400, 510, 100)
    p.drawCentredString(300, 405, "ESPACIO PARA ANOTACIONES ADICIONALES DEL INSPECTOR")
    p.line(200, 150, 400, 150); p.drawCentredString(300, 135, "FIRMA DEL INSPECTOR DE CAMPO")
    p.showPage(); p.save(); buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
