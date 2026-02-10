import os
import django
import sys
from datetime import date
import random

# Agregamos la ruta actual al sistema para que encuentre el módulo 'cementerio'
sys.path.append(os.getcwd())

# Configuración de Django - Asegúrate que este sea el nombre de tu carpeta de configuración
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio.settings')

try:
    django.setup()
    from registros.models import Nicho, RegistroDifunto, Estado
    print("✅ Conexión con Django establecida correctamente.")
except Exception as e:
    print(f"❌ Error al conectar con Django: {e}")
    sys.exit()

def cargar():
    try:
        estado_ocupado = Estado.objects.get(nombre='OCUPADO')
    except Estado.DoesNotExist:
        print("❌ Error: El estado 'OCUPADO' no existe en la base de datos.")
        return

    datos = [
        ("Ricardo Antonio Mejía", "NI-0100"),
        ("Elena Patricia Sosa", "NI-0250"),
        ("Gustavo Adolfo Lemus", "NI-0500"),
        ("Marta Lidia Quiñónez", "NI-1000"),
        ("Brenda Leticia Ruano", "NI-0010"),
        ("Oscar René Valdez", "NI-0800"),
        ("Silvia Marina Castillo", "NI-0300"),
        ("Jorge Mario Estrada", "NI-1200"),
        ("Héctor Manuel Duarte", "NI-0050"),
        ("Sandra Elizabeth Ramos", "NI-0600"),
    ]

    for nombre, codigo in datos:
        nicho = Nicho.objects.filter(codigo=codigo).first()
        if nicho:
            if not RegistroDifunto.objects.filter(nicho=nicho).exists():
                RegistroDifunto.objects.create(
                    nombre_completo=nombre,
                    nicho=nicho,
                    fecha_fallecimiento=date(2025, random.randint(1,12), random.randint(1,28))
                )
                nicho.estado = estado_ocupado
                nicho.save()
                print(f"✅ Registrado: {nombre} en {codigo}")
            else:
                print(f"⚠️ {codigo} ya ocupado.")
        else:
            print(f"❓ Nicho {codigo} no encontrado (se requiere creación previa).")

if __name__ == "__main__":
    cargar()
