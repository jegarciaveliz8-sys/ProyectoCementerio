import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoCementerio.settings')
django.setup()

from registros.models import Nicho

# Coordenadas exactas sobre los techos de los pabellones de Sanarate
pabellones = {
    "Sector A": {"ini": (14.78318, -90.20465), "ancho": 10},
    "Sector B": {"ini": (14.78260, -90.20520), "ancho": 8},
    "Sector C": {"ini": (14.78355, -90.20400), "ancho": 12},
    "Sector D": {"ini": (14.78225, -90.20430), "ancho": 10},
}

actualizados = []
for nombre, data in pabellones.items():
    nichos = Nicho.objects.filter(nivel__sector__nombre=nombre)
    lat_ini, lng_ini = data["ini"]
    for i, n in enumerate(nichos):
        fila = i // data["ancho"]
        col = i % data["ancho"]
        # Espaciado milimétrico para evitar torres
        n.latitud = lat_ini - (fila * 0.00002)
        n.longitud = lng_ini + (col * 0.000025)
        actualizados.append(n)

if actualizados:
    Nicho.objects.bulk_update(actualizados, ['latitud', 'longitud'])
    print(f"✅ ¡PROCESO COMPLETADO! {len(actualizados)} nichos ordenados en bloques reales.")
else:
    print("❌ No se encontraron nichos para actualizar.")
