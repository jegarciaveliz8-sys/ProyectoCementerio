from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Nicho
import json

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
    return JsonResponse({'mensaje': 'Funcion de busqueda'})

def generar_titulo_pdf(request, nicho_id):
    # Esta es la funcion que faltaba y causaba el error
    return HttpResponse(f"Generando PDF para el nicho {nicho_id}...")
