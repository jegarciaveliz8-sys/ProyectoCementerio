import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

# Punto de inicio (Entrada del cementerio)
LAT_INICIO = 14.782270
LNG_INICIO = -90.204500

print("Organizando nichos por filas y columnas...")

# Configuramos bloques de 20 nichos por fila (típico de un pabellón)
nichos = Nicho.objects.all().order_by('codigo')
separacion_h = 0.000015 # Espacio horizontal
separacion_v = 0.000025 # Espacio vertical

for i, nicho in enumerate(nichos):
    columna = i % 20
    fila = i // 20
    
    # Cada 100 nichos (5 filas), dejamos un espacio para un pasillo/calle
    pasillo = (fila // 5) * 0.00005
    
    nicho.lat = LAT_INICIO - (fila * separacion_v) - pasillo
    nicho.lng = LNG_INICIO + (columna * separacion_h)
    nicho.save()

print("✅ ¡Listo! Los 10,000 nichos ahora tienen coordenadas individuales y ordenadas.")
