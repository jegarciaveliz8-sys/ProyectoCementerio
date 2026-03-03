from django.db import models
from auditlog.registry import auditlog # EL ESPÍA

class Nicho(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    propietario = models.CharField(max_length=200, blank=True, null=True)
    nombre_difunto = models.CharField(max_length=200, blank=True, null=True)
    monto_arbitrio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_pago = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    foto_nicho = models.ImageField(upload_to='fotos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrs/', blank=True, null=True)
    esta_exhumado = models.BooleanField(default=False)
    acta_exhumacion = models.FileField(upload_to='actas/', null=True, blank=True)
    notas_legales = models.TextField(null=True, blank=True)
    # ... (tus otros campos)

# AQUÍ SE ACTIVA LA MAGIA
auditlog.register(Nicho)
