from django.shortcuts import render
from .models import Nicho
import json
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def mapa_nichos(request):
    # Filtramos los que tienen coordenadas reales
    referencias = Nicho.objects.exclude(lat=0).exclude(lng=0).exclude(lat=14.78220)
    
    listos_data = []
    for n in referencias:
        listos_data.append({
            'id': n.id,
            'codigo': n.codigo,
            'lat': n.lat,
            'lng': n.lng,
            'difunto': (n.nombre_difunto or "DISPONIBLE").upper(),
            'propietario': (n.propietario or "SIN REGISTRO").upper()
        })

    return render(request, 'registros/mapa.html', {
        'listos_json': json.dumps(listos_data),
    })

def buscar_nicho_json(request):
    codigo = request.GET.get('codigo', '')
    try:
        n = Nicho.objects.get(codigo=codigo)
        return JsonResponse({
            'status': 'ok', 
            'id': n.id,
            'codigo': n.codigo, 
            'lat': n.lat, 
            'lng': n.lng,
            'difunto': n.nombre_difunto or "DISPONIBLE"
        })
    except Nicho.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No encontrado'})

@csrf_exempt
def actualizar_posicion(request):
    return JsonResponse({'status': 'error', 'message': 'SISTEMA BLINDADO: No se permiten cambios'}, status=403)

def generar_titulo_pdf(request, nicho_id):
    try:
        n = Nicho.objects.get(id=nicho_id)
    except Nicho.DoesNotExist:
        return HttpResponse("Error: Nicho no encontrado", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Titulo_{n.codigo}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    ancho, alto = letter

    # --- DISEÑO DEL TÍTULO OFICIAL ---
    p.setLineWidth(2)
    p.rect(0.5*inch, 0.5*inch, 7.5*inch, 10*inch)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(ancho/2, 9.7*inch, "MUNICIPALIDAD DE SANARATE, EL PROGRESO")
    p.setFont("Helvetica", 12)
    p.drawCentredString(ancho/2, 9.4*inch, "ADMINISTRACIÓN DE CEMENTERIO MUNICIPAL")
    
    p.line(1*inch, 9.2*inch, 7.5*inch, 9.2*inch)

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ancho/2, 8.5*inch, "TÍTULO DE PROPIEDAD Y PERPETUIDAD")

    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 7.5*inch, f"CÓDIGO DE REGISTRO: {n.codigo}")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1*inch, 7.0*inch, f"DIFUNTO: {(n.nombre_difunto or 'DISPONIBLE').upper()}")
    
    p.setFont("Helvetica", 12)
    p.drawString(1*inch, 6.5*inch, f"PROPIETARIO: {(n.propietario or 'SIN REGISTRO').upper()}")
    p.drawString(1*inch, 6.0*inch, f"UBICACIÓN GPS: {n.lat}, {n.lng}")

    p.drawString(1*inch, 4.5*inch, "Este documento legaliza la estancia del difunto en el campo santo municipal.")

    # Firmas
    p.line(1.5*inch, 2.5*inch, 3.5*inch, 2.5*inch)
    p.drawCentredString(2.5*inch, 2.3*inch, "Encargado de Cementerio")
    p.line(5*inch, 2.5*inch, 7*inch, 2.5*inch)
    p.drawCentredString(6*inch, 2.3*inch, "Secretario Municipal")

    p.showPage()
    p.save()
    return response

from django.shortcuts import render, redirect
from .models import FotoCampo, Nicho

def registro_campo_offline(request):
    if request.method == 'POST':
        nicho_id = request.POST.get('nicho_id')
        imagen = request.FILES.get('imagen')
        comentario = request.POST.get('comentario')
        
        if nicho_id and imagen:
            nicho = Nicho.objects.get(id=nicho_id)
            FotoCampo.objects.create(nicho=nicho, imagen=imagen, comentario=comentario)
            return render(request, 'registros/registro_exitoso.html')
            
    nichos = Nicho.objects.all().order_by('codigo')
    return render(request, 'registros/offline_form.html', {'nichos': nichos})
