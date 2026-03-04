from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from .models import Nicho

def dashboard(request):
    total = Nicho.objects.count()
    ocupados = Nicho.objects.exclude(nombre_difunto__isnull=True).exclude(nombre_difunto="").count()
    disponibles = total - ocupados
    mora_count = Nicho.objects.filter(monto_arbitrio__lte=0).exclude(nombre_difunto="").count()
    recaudado = Nicho.objects.aggregate(Sum('monto_arbitrio'))['monto_arbitrio__sum'] or 0
    
    context = {
        'total': total,
        'ocupados': ocupados,
        'disponibles': disponibles,
        'mora_total': mora_count,
        'recaudado': recaudado,
    }
    return render(request, 'registros/dashboard.html', context)

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
            'foto_url': n.foto_nicho.url if n.foto_nicho else None,
        })
    return JsonResponse(data, safe=False)

def imprimir_ficha(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return render(request, 'registros/ficha_impresion.html', {'nicho': nicho})

def imprimir_todos_qrs(request):
    # Traemos solo los nichos que tienen un QR generado
    nichos = Nicho.objects.exclude(qr_code__isnull=True).exclude(qr_code='')
    return render(request, 'registros/imprimir_qrs.html', {'nichos': nichos})
