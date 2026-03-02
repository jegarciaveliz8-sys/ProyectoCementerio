import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoCementerio.settings')
django.setup()

from registros.models import Nicho, Exhumacion

def cargar_pruebas():
    # Buscamos 3 nichos para la prueba
    nichos = Nicho.objects.all()[:3]
    
    if nichos.count() < 3:
        print("❌ Error: Necesitas al menos 3 nichos en la base de datos.")
        return

    casos = [
        {
            'acta': 'ACTA-2026-001',
            'oficio': 'MSPAS-SAN-045',
            'difunto': 'Juan Alberto Méndez',
            'solicitante': 'María Méndez (Hija)',
            'dpi': '2345 67890 0101',
            'destino': 'Osario General Sector B',
            'autorizado': 'Secretario Municipal',
            'obs': 'Exhumación por cumplimiento de tiempo (6 años) sin renovación.'
        },
        {
            'acta': 'ACTA-2026-002',
            'oficio': 'MSPAS-SAN-089',
            'difunto': 'Ricardo Arriola Paz',
            'solicitante': 'Juzgado de Paz Sanarate',
            'dpi': 'OFICIO-JUD-99',
            'destino': 'Traslado a Cementerio Privado',
            'autorizado': 'Administrador del Cementerio',
            'obs': 'Orden judicial para estudio forense y posterior traslado.'
        },
        {
            'acta': 'ACTA-2026-005',
            'oficio': 'N/A',
            'difunto': 'Elena Rosales',
            'solicitante': 'Pedro Rosales (Esposo)',
            'dpi': '1122 33445 0202',
            'destino': 'Mausoleo Familiar Capilla 1',
            'autorizado': 'Alcalde Municipal',
            'obs': 'Traslado solicitado por la familia por mejora de nicho.'
        }
    ]

    for i, datos in enumerate(casos):
        n = nichos[i]
        Exhumacion.objects.create(
            nicho=n,
            no_acta_municipal=datos['acta'],
            no_oficio_salud=datos['oficio'],
            fecha_exhumacion=datetime.date.today(),
            nombre_difunto_retirado=datos['difunto'],
            solicitante=datos['solicitante'],
            dpi_solicitante=datos['dpi'],
            destino_restos=datos['destino'],
            autorizado_por=datos['autorizado'],
            observaciones=datos['obs']
        )
        print(f"✅ Exhumación creada para: {datos['difunto']} en Nicho {n.codigo}")

if __name__ == "__main__":
    cargar_pruebas()
