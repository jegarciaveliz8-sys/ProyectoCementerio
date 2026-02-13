from django.shortcuts import render, get_object_or_404
from .models import Nicho, FotoCampo, Exhumacion
import json, os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.utils import timezone

# Ruta global del logo para las funciones de PDF
LOGO_PATH = os.path.join(settings.BASE_DIR, 'registros', 'static', 'img', 'logo_muni.png')

def mapa_nichos(request):
    nicho_id = request.GET.get('id', 0) 
    referencias = Nicho.objects.exclude(lat=0).exclude(lng=0).exclude(lat=14.7822).exclude(lat=14.78220)
    hoy = timezone.now().date()
    listos_data = []
    
    for n in referencias:
        if n.estado_id == 1: color_punto = "green"
        elif n.fecha_vencimiento and n.fecha_vencimiento < hoy: color_punto = "red"
        elif n.estado_id == 3: color_punto = "orange"
        else: color_punto = "blue"
            
        listos_data.append({
            'id': str(n.id),
            'codigo': n.codigo,
            'lat': float(n.lat),
            'lng': float(n.lng),
            'difunto': (n.nombre_difunto or "DISPONIBLE").upper(),
            'propietario': (n.propietario or "SIN REGISTRO").upper(),
            'color': color_punto,
            'vencimiento': str(n.fecha_vencimiento) if n.fecha_vencimiento else "N/A"
        })

    return render(request, 'registros/mapa.html', {
        'listos_json': json.dumps(listos_data),
        'nicho_seleccionado': str(nicho_id),
    })

def buscar_nicho_json(request):
    codigo = request.GET.get('codigo', '')
    try:
        n = Nicho.objects.get(codigo=codigo)
        return JsonResponse({'status': 'ok', 'id': n.id, 'codigo': n.codigo, 'lat': n.lat, 'lng': n.lng, 'difunto': n.nombre_difunto or "DISPONIBLE"})
    except Nicho.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No encontrado'})

@csrf_exempt
def actualizar_posicion(request):
    return JsonResponse({'status': 'error', 'message': 'SISTEMA BLINDADO'}, status=403)

def generar_titulo_pdf(request, nicho_id):
    n = get_object_or_404(Nicho, id=nicho_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Titulo_{n.codigo}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    ancho, alto = letter
    
    # 1. Marco y Logo
    p.setLineWidth(2)
    p.rect(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
    
    if os.path.exists(LOGO_PATH):
        p.drawImage(LOGO_PATH, 0.7*inch, 9.2*inch, width=0.8*inch, height=0.8*inch, mask='auto')

    # 2. QR
    datos_qr = f"Nicho:{n.codigo}|DPI:{n.dpi_propietario or 'S/D'}"
    url_qr = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={datos_qr}"
    p.drawImage(url_qr, 7.0*inch, 9.15*inch, width=0.85*inch, height=0.85*inch)

    # 3. Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(ancho/2, 9.7*inch, "MUNICIPALIDAD DE SANARATE, EL PROGRESO")
    p.setFont("Helvetica", 12)
    p.drawCentredString(ancho/2, 9.4*inch, "ADMINISTRACIÓN DE CEMENTERIO MUNICIPAL")
    p.setLineWidth(1)
    p.line(1.6*inch, 9.25*inch, 6.8*inch, 9.25*inch) 

    # 4. Contenido
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ancho/2, 8.2*inch, "TÍTULO DE PROPIEDAD Y PERPETUIDAD")
    p.setFont("Helvetica", 12)
    p.drawString(1.2*inch, 7.3*inch, f"CÓDIGO DE REGISTRO: {n.codigo}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1.2*inch, 6.8*inch, f"DIFUNTO: {(n.nombre_difunto or 'RESERVA').upper()}")
    p.setFont("Helvetica", 12)
    p.drawString(1.2*inch, 6.3*inch, f"PROPIETARIO: {(n.propietario or 'SIN REGISTRO').upper()}")
    p.drawString(1.2*inch, 5.8*inch, f"UBICACIÓN GPS: {n.lat}, {n.lng}")

    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(ancho/2, 4.5*inch, "Este documento legaliza la estancia del difunto en el campo santo municipal.")

    # 5. Firmas
    p.line(1.5*inch, 2.5*inch, 3.5*inch, 2.5*inch)
    p.drawCentredString(2.5*inch, 2.3*inch, "Encargado de Cementerio")
    p.line(5*inch, 2.5*inch, 7*inch, 2.5*inch)
    p.drawCentredString(6*inch, 2.3*inch, "Secretario Municipal")

    p.showPage()
    p.save()
    return response

def registro_campo_offline(request):
    if request.method == 'POST':
        nicho_id = request.POST.get('nicho_id')
        imagen = request.FILES.get('imagen')
        if nicho_id and imagen:
            nicho = Nicho.objects.get(id=nicho_id)
            FotoCampo.objects.create(nicho=nicho, imagen=imagen, comentario=request.POST.get('comentario', ''))
            return render(request, 'registros/registro_exitoso.html')
    nichos = Nicho.objects.all().order_by('codigo')
    return render(request, 'registros/offline_form.html', {'nichos': nichos})

def generar_acta_exhumacion_pdf(request, exhumacion_id):
    exhumacion = get_object_or_404(Exhumacion, id=exhumacion_id)
    nicho = exhumacion.nicho
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ACTA_EXHUMACION_{nicho.codigo}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    ancho, alto = letter
    
    p.setLineWidth(2)
    p.rect(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
    
    if os.path.exists(LOGO_PATH):
        p.drawImage(LOGO_PATH, 0.7*inch, 9.2*inch, width=0.8*inch, height=0.8*inch, mask='auto')

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(ancho/2, 9.7*inch, "MUNICIPALIDAD DE SANARATE, EL PROGRESO")
    p.setFont("Helvetica", 12)
    p.drawCentredString(ancho/2, 9.4*inch, "REGISTRO CIVIL Y DE CEMENTERIOS")
    p.line(1.6*inch, 9.2*inch, 7.5*inch, 9.2*inch)
    
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ancho/2, 8.5*inch, "ACTA DE EXHUMACIÓN")
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 7.5*inch, f"CÓDIGO DE NICHO: {nicho.codigo}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, 6.5*inch, f"DIFUNTO RETIRADO: {exhumacion.nombre_difunto_retirado.upper()}")
    
    p.showPage()
    p.save()
    return response
