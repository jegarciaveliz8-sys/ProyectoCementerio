import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cementerio_config.settings')
django.setup()

from registros.models import Nicho, Pago, RegistroDifunto

def generar_reporte():
    hace_una_semana = datetime.now() - timedelta(days=7)
    
    # 1. Cálculos de la semana
    nuevos_difuntos = RegistroDifunto.objects.filter(fecha_entierro__gte=hace_una_semana).count()
    recaudacion = Pago.objects.filter(fecha_pago__gte=hace_una_semana).aggregate(django.db.models.Sum('monto'))['monto__sum'] or 0
    total_ocupados = Nicho.objects.filter(estado__nombre="OCUPADO").count()
    
    reporte = f"""
    📊 REPORTE SEMANAL - CEMENTERIO DE SANARATE
    -------------------------------------------
    Fecha: {datetime.now().strftime('%d/%m/%Y')}
    
    ✅ Nuevas Inhumaciones (7 días): {nuevos_difuntos}
    💰 Recaudación de la semana: Q {recaudacion:.2f}
    📍 Ocupación Total Actual: {total_ocupados} nichos
    -------------------------------------------
    """
    print(reporte)
    # Aquí podrías agregar la función de enviar email si tienes el servidor SMTP configurado.

if __name__ == "__main__":
    generar_reporte()
