import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def cargar():
    archivo = 'coordenadas_reales_sanarate.json'
    if not os.path.exists(archivo):
        print("❌ Archivo no encontrado.")
        return

    with open(archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print(f"📡 Analizando {len(datos)} registros tipo Fixture...")
    actualizados = 0
    errores = 0

    for item in datos:
        # En los fixtures de Django, los datos están dentro de 'fields'
        fields = item.get('fields', {})
        codigo = fields.get('codigo')
        lat = fields.get('lat')
        lng = fields.get('lng')

        if codigo and lat is not None and lng is not None:
            # Buscamos y actualizamos
            filas = Nicho.objects.filter(codigo=codigo).update(lat=lat, lng=lng)
            if filas > 0:
                actualizados += 1
            else:
                errores += 1

    print(f"\n✅ ¡PROCESO EXITOSO!")
    print(f"📍 Nichos georeferenciados: {actualizados}")
    print(f"⚠️ Códigos no encontrados en tu DB actual: {errores}")

if __name__ == '__main__':
    cargar()
