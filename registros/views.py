from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
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
    nichos = Nicho.objects.all()
    data = [{'id': n.id, 'codigo': n.codigo, 'nombre_difunto': n.nombre_difunto, 'lat': n.lat, 'lng': n.lng, 'monto_arbitrio': float(n.monto_arbitrio)} for n in nichos]
    return JsonResponse(data, safe=False)

def imprimir_ficha(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return render(request, 'registros/ficha_impresion.html', {'nicho': nicho})

def imprimir_todos_qrs(request):
    nichos = Nicho.objects.exclude(qr_code__isnull=True).exclude(qr_code='')
    return render(request, 'registros/imprimir_qrs.html', {'nichos': nichos})

def generar_titulo_propiedad(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    sello = nicho.generar_sello_seguridad()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # MARCA DE AGUA
    p.saveState()
    p.setFont("Helvetica-Bold", 40)
    p.setFillColor(colors.lightgrey, alpha=0.1)
    p.translate(300, 400); p.rotate(45)
    p.drawCentredString(0, 0, f"AUTÉNTICO: {sello}")
    p.restoreState()

    # --- RUTA DEL LOGO (Confirmada por ls) ---
    logo_path = os.path.join(settings.BASE_DIR, 'registros', 'static', 'img', 'logo_muni.png')
    
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 45, 680, width=70, height=70, mask='auto')

    # ENCABEZADO
    p.setStrokeColor(colors.black); p.setLineWidth(2)
    p.rect(30, 30, 550, 730)
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(325, 715, "MUNICIPALIDAD DE SANARATE")
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(325, 700, "DEPARTAMENTO DE CONTROL DE CEMENTERIOS")
    p.line(50, 675, 550, 675)
    
    # CUERPO
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(300, 620, "TÍTULO DE PROPIEDAD DE NICHO PERPETUO")
    p.setFont("Helvetica", 12)
    p.drawString(70, 570, "POR EL PRESENTE SE HACE CONSTAR QUE:")
    p.setFont("Helvetica-Bold", 15)
    p.drawCentredString(300, 545, f"{nicho.propietario or 'S/P'}")
    p.setFont("Helvetica", 11)
    p.drawString(70, 500, f"Es propietario legítimo del nicho código: {nicho.codigo}")
    p.drawString(70, 475, f"Restos de: {nicho.nombre_difunto or 'DISPONIBLE'}")
    
    # VALIDACIÓN Y QR
    p.setDash(1, 2); p.line(70, 160, 530, 160); p.setDash()
    p.setFont("Helvetica-Bold", 9)
    p.drawString(70, 145, "CÓDIGO ÚNICO DE VALIDACIÓN (CVE):")
    p.setFont("Courier-Bold", 11); p.setFillColor(colors.darkblue)
    p.drawString(70, 130, f"{sello}")
    
    if nicho.qr_code:
        p.drawImage(nicho.qr_code.path, 460, 50, width=80, height=80)

    p.setFillColor(colors.black); p.setFont("Helvetica-Oblique", 7)
    p.drawCentredString(300, 40, f"Documento oficial generado por el Sistema G.I.S. Sanarate")
    p.drawCentredString(300, 32, f"ID Registro: {nicho.id} | Fecha de Emisión: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")

    p.showPage(); p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

def consulta_publica(request, codigo):
    nicho = get_object_or_404(Nicho, codigo=codigo)
    
    # Lógica de semáforo: Mora por arbitrio o por fecha vencida
    es_moroso = nicho.monto_arbitrio <= 0
    dias_vencido = 0
    if nicho.fecha_vencimiento and nicho.fecha_vencimiento < timezone.now().date():
        dias_vencido = (timezone.now().date() - nicho.fecha_vencimiento).days
        es_moroso = True  # Si la fecha ya pasó, también es mora

    context = {
        'nicho': nicho,
        'es_moroso': es_moroso,
        'dias_vencido': dias_vencido,
        'fecha_servidor': timezone.now(),
    }
    return render(request, 'registros/consulta_inspector.html', context)
