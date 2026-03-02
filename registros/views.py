from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Nicho, Exhumacion
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

# 1. EL MAPA PRINCIPAL (Usando 'lat' en lugar de 'latitud')
def mapa_nichos(request):
    nichos = Nicho.objects.exclude(lat=0).exclude(lat__isnull=True)
    return render(request, 'registros/mapa_final.html', {'nichos': nichos})

# 2. EL BUSCADOR DEL MAPA
def buscar_nicho_json(request):
    codigo = request.GET.get('codigo', '')
    try:
        nicho = Nicho.objects.get(codigo=codigo)
        return JsonResponse({
            'id': nicho.id,
            'codigo': nicho.codigo,
            'nombre_difunto': nicho.nombre_difunto or "SIN REGISTRO",
            'propietario': nicho.propietario or "SIN REGISTRO",
            'latitud': nicho.lat,  # Enviamos 'lat' al mapa
            'longitud': nicho.lng, # Enviamos 'lng' al mapa
        })
    except Nicho.DoesNotExist:
        return JsonResponse({'error': 'No existe'}, status=404)

# 3. GENERACIÓN DE TÍTULOS
def generar_titulo_pdf(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"TITULO: {nicho.codigo}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# 4. ACTAS DE EXHUMACIÓN
def generar_acta_exhumacion_pdf(request, exhumacion_id):
    exhumacion = get_object_or_404(Exhumacion, id=exhumacion_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"ACTA EXHUMACION: {exhumacion.id}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# 5. REGISTRO DE CAMPO OFFLINE
def registro_campo_offline(request):
    return render(request, 'registros/registro_campo.html')

