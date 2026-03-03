import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def generar():
    print("🚀 Generando 100 nichos de prueba en Sanarate...")
    for i in range(1, 101):
        codigo = f"N-PROBA-{i:03d}"
        # Coordenadas aproximadas de Sanarate
        lat = 14.78 + (random.uniform(-0.005, 0.005))
        lng = -90.19 + (random.uniform(-0.005, 0.005))
        
        Nicho.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre_difunto': f'DIFUNTO PRUEBA {i}',
                'propietario': f'FAMILIA PRUEBA {i}',
                'lat': lat,
                'lng': lng,
                'monto_arbitrio': 150.00
            }
        )
    print("✅ ¡Listo! 100 nichos creados.")

if __name__ == '__main__':
    generar()
