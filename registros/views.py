from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Nicho

def mapa_cimenterio(request):
    nichos = Nicho.objects.exclude(lat__isnull=True).exclude(lng__isnull=True)
    return render(request, 'registros/mapa.html', {'nichos': nichos})

def datos_nichos_json(request):
    # Agregamos 'id' para que el mapa pueda crear enlaces directos al Admin
    nichos = Nicho.objects.all().values(
        'id', 'codigo', 'nombre_difunto', 'lat', 'lng', 
        'esta_exhumado', 'monto_arbitrio'
    )
    return JsonResponse(list(nichos), safe=False)

def imprimir_ficha(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return render(request, 'registros/ficha_impresion.html', {'nicho': nicho})
