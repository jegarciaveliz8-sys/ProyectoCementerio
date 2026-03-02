import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho

def activar():
    print("⏳ Procesando 9,998 nichos... Esto tomará unos segundos.")
    hoy = timezone.now().date()
    
    # 1. Ponemos Q100 a los ocupados que tienen el monto en 0
    ocupados = Nicho.objects.exclude(nombre_difunto__icontains='DISPONIBLE').exclude(nombre_difunto__icontains='LIBRE')
    actualizados = ocupados.update(monto_arbitrio=100.00)
    
    # 2. Contamos morosos reales para estar seguros
    morosos = Nicho.objects.filter(fecha_vencimiento__lt=hoy).count()
    
    print(f"✅ ¡Éxito! {actualizados} nichos ahora tienen arbitrio de Q100.")
    print(f"🚨 Se detectaron {morosos} nichos en mora.")

if __name__ == '__main__':
    activar()
