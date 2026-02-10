import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Edificio, Nicho, Nivel, EstadoNicho, Sector

def cargar_todo():
    print("🧹 Limpiando registros previos para evitar duplicados...")
    Nicho.objects.all().delete()
    
    print("🚀 Iniciando carga masiva de 5,000 registros...")
    
    estado_obj, _ = EstadoNicho.objects.get_or_create(nombre="DISPONIBLE")

    sectores_config = [
        {"nombre": "Pabellón Municipal Norte", "lat": 14.7825, "lon": -90.2010, "prefijo": "PMN"},
        {"nombre": "Pabellón San Juan", "lat": 14.7830, "lon": -90.2015, "prefijo": "PSJ"},
        {"nombre": "Pabellón de los Ángeles", "lat": 14.7828, "lon": -90.2020, "prefijo": "PLA"},
        {"nombre": "Sector General Este", "lat": 14.7822, "lon": -90.2012, "prefijo": "SGE"},
        {"nombre": "Mausoleos del Recuerdo", "lat": 14.7835, "lon": -90.2018, "prefijo": "MDR"},
    ]

    for s in sectores_config:
        edificio, _ = Edificio.objects.get_or_create(
            nombre=s["nombre"],
            defaults={"latitud": s["lat"], "longitud": s["lon"]}
        )

        sector_obj, _ = Sector.objects.get_or_create(
            nombre=f"Sección Única - {s['nombre']}",
            edificio=edificio
        )

        nivel_obj, _ = Nivel.objects.get_or_create(
            nombre="Nivel General",
            sector=sector_obj
        )
        
        print(f"📦 Creando 1,000 nichos en {s['nombre']}...")
        nichos_bulk = []
        for i in range(1, 1001):
            # Usamos el prefijo para asegurar que cada código sea único a nivel mundial
            codigo_nicho = f"{s['prefijo']}-{i:04d}"
            nichos_bulk.append(Nicho(
                codigo=codigo_nicho,
                nivel=nivel_obj,
                estado=estado_obj
            ))
        
        Nicho.objects.bulk_create(nichos_bulk)

    print("✅ ¡EXITO TOTAL! 5,000 nichos únicos creados en Sanarate.")

if __name__ == "__main__":
    cargar_todo()
