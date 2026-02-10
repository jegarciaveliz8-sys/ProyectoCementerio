import os
import django

# Esto detecta automáticamente tus carpetas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings') 
try:
    django.setup()
except:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoCementerio.settings')
    django.setup()

from registros.models import Nicho

# Coordenadas maestras de Sanarate (Satelital)
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
        # Distribución cuadrada: pequeña en latitud, un poco más en longitud
        n.latitud = lat_ini - (fila * 0.000018)
        n.longitud = lng_ini + (col * 0.000022)
        actualizados.append(n)

if actualizados:
    Nicho.objects.bulk_update(actualizados, ['latitud', 'longitud'])
    print(f"✅ ¡LISTO! {len(actualizados)} nichos organizados sobre el cementerio.")
else:
    print("❌ No se encontraron nichos. Revisa los nombres de los sectores.")
