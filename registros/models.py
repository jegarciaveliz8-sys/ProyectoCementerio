from django.db import models
from auditlog.registry import auditlog
import qrcode
from io import BytesIO
from django.core.files import File

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

    def __str__(self):
        return f"{self.codigo} - {self.nombre_difunto or 'Disponible'}"

    # --- MOTOR DE GENERACIÓN AUTOMÁTICA DE QR ---
    def save(self, *args, **kwargs):
        # Si no tiene QR, lo generamos automáticamente
        if not self.qr_code:
            # Creamos el QR con el código del nicho
            # Esto puede ser una URL o solo el código
            qr_data = f"Nicho: {self.codigo} | Propietario: {self.propietario}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            # Guardamos el archivo generado en el campo qr_code
            filename = f'qr_{self.codigo}.png'
            self.qr_code.save(filename, File(buffer), save=False)
            
        super().save(*args, **kwargs)

# REGISTRO DEL ESPÍA (Auditoría)
auditlog.register(Nicho)
