import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def cargar():
    # Buscamos el archivo en tu carpeta
    ruta_json = 'coordenadas_reales_sanarate.json'
    
    if not os.path.exists(ruta_json):
        print(f"❌ Error: No encuentro el archivo {ruta_json}")
        return

    with open(ruta_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print(f"📡 Procesando {len(datos)} coordenadas...")
    actualizados = 0
    errores = 0

    for item in datos:
        codigo = item.get('codigo')
        lat = item.get('lat')
        lng = item.get('lng')

        if codigo and lat and lng:
            # Buscamos el nicho por código y le clavamos el GPS
            # Usamos filter().update() para que sea veloz (masivo)
            filas = Nicho.objects.filter(codigo=codigo).update(lat=lat, lng=lng)
            if filas > 0:
                actualizados += 1
            else:
                errores += 1

    print(f"✅ ¡Proceso terminado!")
    print(f"📍 Nichos georeferenciados: {actualizados}")
    print(f"⚠️ Códigos no encontrados en la base: {errores}")

if __name__ == '__main__':
    cargar()
