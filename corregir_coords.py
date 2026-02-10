import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

# Coordenadas centrales del Cementerio de Sanarate
LAT_REAL = 14.782270
LNG_REAL = -90.204500

print("Corrigiendo coordenadas de 10,000 nichos...")
for i, nicho in enumerate(Nicho.objects.all()):
    # Espaciamos los nichos un poquito para que no queden todos en el mismo pixel
    nicho.lat = LAT_REAL + (i * 0.000001) 
    nicho.lng = LNG_REAL + (i * 0.000001)
    nicho.save()

print("¡Listo! Todos los nichos fueron movidos al Cementerio de Sanarate.")
