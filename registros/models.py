from django.db import models
from auditlog.registry import auditlog
import qrcode
import hashlib
import os
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from datetime import timedelta

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

    def generar_sello_seguridad(self):
        seed = f"{self.codigo}-{self.propietario}-{self.fecha_vencimiento}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16].upper()

    @property
    def semaforo_estado(self):
        if self.esta_exhumado:
            return {'estado': 'EXHUMADO', 'color': '#6c757d', 'prioridad': 0}
        if not self.fecha_vencimiento:
            return {'estado': 'SIN FECHA', 'color': '#17a2b8', 'prioridad': 0}
        hoy = timezone.now().date()
        mora = hoy - self.fecha_vencimiento
        if mora.days <= 0:
            return {'estado': 'AL DÍA', 'color': '#28a745', 'prioridad': 1}
        elif 0 < mora.days <= 90:
            return {'estado': 'MORA RECIENTE', 'color': '#ffc107', 'prioridad': 2}
        elif 90 < mora.days <= 365:
            return {'estado': 'PRE-EXHUMACIÓN', 'color': '#fd7e14', 'prioridad': 3}
        else:
            return {'estado': 'SUJETO A EXHUMACIÓN', 'color': '#dc3545', 'prioridad': 4}

    def save(self, *args, **kwargs):
        # 1. Preparar la data del QR
        sello = self.generar_sello_seguridad()
        qr_text = f"ID: {self.codigo} | Difunto: {self.nombre_difunto or 'N/A'} | Sello: {sello}"
        
        # 2. Generar la imagen del QR en memoria
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.codigo}.png'

        # 3. Guardar el archivo QR sin disparar save() recursivo
        # Guardamos el archivo en el campo, pero save=False es clave
        self.qr_code.save(filename, File(buffer), save=False)
        
        # 4. Guardado final de la base de datos
        super().save(*args, **kwargs)

class ReporteDano(models.Model):
    ESTADOS = [('PENDIENTE', '🔴 Pendiente'), ('EN_PROCESO', '🟡 En Proceso'), ('RESUELTO', '🟢 Resuelto')]
    NIVELES = [('LEVE', 'Leve'), ('MODERADO', 'Moderado'), ('CRITICO', 'Crítico')]
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='reportes_danos')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    nivel_urgencia = models.CharField(max_length=10, choices=NIVELES, default='LEVE')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    reportado_por = models.CharField(max_length=100)
    foto_evidencia = models.ImageField(upload_to='danos/', blank=True, null=True)

    class Meta:
        verbose_name = "Reporte de Daño"
        verbose_name_plural = "Control de Daños"

auditlog.register(Nicho)
auditlog.register(ReporteDano)
