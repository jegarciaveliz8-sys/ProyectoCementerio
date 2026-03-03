from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Nicho

def mapa_cimenterio(request):
    nichos = Nicho.objects.exclude(lat__isnull=True).exclude(lng__isnull=True)
    return render(request, 'registros/mapa.html', {'nichos': nichos})

def datos_nichos_json(request):
    nichos = Nicho.objects.all()
    data = []
    for n in nichos:
        data.append({
            'id': n.id,
            'codigo': n.codigo,
            'nombre_difunto': n.nombre_difunto,
            'lat': n.lat,
            'lng': n.lng,
            'esta_exhumado': n.esta_exhumado,
            'monto_arbitrio': float(n.monto_arbitrio),
            # AQUÍ ESTÁ LA MAGIA: Si tiene foto, manda el link de Cloudinary
            'foto_url': n.foto_nicho.url if n.foto_nicho else None,
        })
    return JsonResponse(data, safe=False)

def imprimir_ficha(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return render(request, 'registros/ficha_impresion.html', {'nicho': nicho})
