from django.db import models
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Nicho
import json

def dashboard_stats(request):
    hoy = timezone.now().date()
    total = Nicho.objects.count()
    ocupados = Nicho.objects.filter(estado_id=2).count()
    disponibles = Nicho.objects.filter(estado_id=1).count()
    vencidos = Nicho.objects.filter(estado_id=2, fecha_vencimiento__lt=hoy).count()
    
    sectores = ['A', 'B', 'C', 'D']
    stats_sectores = []
    for s in sectores:
        n_sector = Nicho.objects.filter(Q(codigo__istartswith=s) | Q(codigo__icontains=f'SECTOR {s}'))
        stats_sectores.append({
            'nombre': s,
            'total': n_sector.count(),
            'ocupados': n_sector.filter(estado_id=2).count(),
            'vencidos': n_sector.filter(estado_id=2, fecha_vencimiento__lt=hoy).count(),
            'libres': n_sector.filter(estado_id=1).count(),
        })

    context = {
        'total': total,
        'ocupados': ocupados,
        'disponibles': disponibles,
        'vencidos': vencidos,
        'stats_sectores': stats_sectores,
        'fecha': hoy,
    }
    return render(request, 'admin/dashboard.html', context)

def mapa_nichos(request):
    nichos = Nicho.objects.all()
    todos_json = [
        {
            'id': n.id,
            'codigo': n.codigo,
            'nombre_difunto': n.nombre_difunto or "DISPONIBLE",
            'lat': float(n.lat) if n.lat else 0,
            'lng': float(n.lng) if n.lng else 0,
        } for n in nichos
    ]
    return render(request, 'registros/mapa.html', {'todos_json': json.dumps(todos_json)})

@csrf_exempt
def actualizar_posicion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nicho = Nicho.objects.get(id=data['id'])
            nicho.lat = data['lat']
            nicho.lng = data['lng']
            nicho.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

def buscar_nicho_json(request):
    query = request.GET.get('q', '')
    nichos = Nicho.objects.filter(codigo__icontains=query)[:10]
    resultados = [{'id': n.id, 'text': n.codigo} for n in nichos]
    return JsonResponse({'results': resultados})

def generar_titulo_pdf(request, nicho_id):
    nicho = get_object_or_404(Nicho, id=nicho_id)
    return HttpResponse(f"<h1>Título de Propiedad - Sanarate</h1><p>Nicho: {nicho.codigo}</p>")

def detalle_nicho_publico(request, codigo):
    nicho = get_object_or_404(Nicho, codigo=codigo)
    return render(request, 'registros/ficha_publica.html', {'nicho': nicho})

def buscador_nichos(request):
    query = request.GET.get('q', '')
    resultados = None
    if query:
        resultados = Nicho.objects.filter(
            Q(codigo__icontains=query) | Q(nombre_difunto__icontains=query)
        )[:20]
    return render(request, 'registros/buscador.html', {'resultados': resultados, 'query': query})
