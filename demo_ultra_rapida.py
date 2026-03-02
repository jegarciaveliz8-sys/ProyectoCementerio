import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def cargar_demo():
    archivo = 'coordenadas_reales_sanarate.json'
    if not os.path.exists(archivo):
        print("❌ Archivo no encontrado.")
        return

    with open(archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print(f"🎯 Preparando Demo Ultra Rápida (Solo Sector A)...")

    # 1. Filtramos solo los primeros 150 del Sector A
    mapeo_demo = {}
    contador = 0
    for item in datos:
        fields = item.get('fields', {})
        codigo = fields.get('codigo', '')
        
        if codigo.startswith('A') and contador < 150:
            mapeo_demo[codigo] = (fields.get('lat'), fields.get('lng'))
            contador += 1

    # 2. Limpiamos coordenadas viejas (opcional, para que la demo se vea limpia)
    print("🧹 Limpiando mapa para la demo...")
    Nicho.objects.all().update(lat=0, lng=0)

    # 3. Aplicamos los 150 puntos seleccionados
    nichos_db = Nicho.objects.filter(codigo__in=mapeo_demo.keys())
    nichos_para_actualizar = []
    
    for nicho in nichos_db:
        lat, lng = mapeo_demo[nicho.codigo]
        nicho.lat = lat
        nicho.lng = lng
        nichos_para_actualizar.append(nicho)

    Nicho.objects.bulk_update(nichos_para_actualizar, ['lat', 'lng'])

    print(f"\n✅ ¡DEMO CARGADA!")
    print(f"📍 Puntos en el mapa: {len(nichos_para_actualizar)}")
    print(f"🚀 Ahora el mapa de Sanarate volará en la presentación.")

if __name__ == '__main__':
    cargar_demo()
