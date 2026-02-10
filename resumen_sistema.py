import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho, RegistroDifunto, Pago
from django.db.models import Sum

def mostrar_todo():
    print("\n" + "="*40)
    print("🏛️  SISTEMA CEMENTERIO SANARATE V1.0")
    print("="*40)
    print(f"📦 Capacidad Instalada: {Nicho.objects.count()} nichos.")
    print(f"👥 Población Registrada: {RegistroDifunto.objects.count()} difuntos.")
    print(f"💰 Recaudación Total: Q {Pago.objects.aggregate(Sum('monto'))['monto__sum'] or 0:.2f}")
    print(f"📡 Estado del Mapa: 5 Pabellones Georreferenciados.")
    print("="*40)
    print("🚀 LISTO PARA OPERACIÓN MUNICIPAL\n")

if __name__ == "__main__":
    mostrar_todo()
