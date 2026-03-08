from django.db import models
from auditlog.registry import auditlog
import qrcode
import hashlib
import os
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

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
    
    numero_acta = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. Acta Actual")
    numero_titulo = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. Título")
    numero_formulario = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. Formulario")
    
    archivo_acta = models.FileField(upload_to='actas/', null=True, blank=True)
    archivo_titulo = models.FileField(upload_to='titulos/', null=True, blank=True)
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
        sello = self.generar_sello_seguridad()
        qr_text = f"ID: {self.codigo} | Difunto: {self.nombre_difunto or 'N/A'} | Sello: {sello}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.codigo}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)

class ActaExhumacion(models.Model):
    TIPOS = [
        ('ADMINISTRATIVA', '🏛️ Municipal (Mora/Vencimiento)'),
        ('JUDICIAL', '⚖️ Judicial (Orden MP/Juez)'),
        ('FAMILIAR', '👨👩👦 Familiar (Voluntaria)'),
        ('SANITARIA', '☣️ Sanitaria (Salud Pública)'),
    ]

    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='historial_actas')
    fecha_proceso = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='ADMINISTRATIVA')
    numero_acta = models.CharField(max_length=50, unique=True, help_text="Ej: ACTA-2026-001")
    solicitante_nombre = models.CharField(max_length=200, verbose_name="Nombre del Requirente")
    solicitante_dpi = models.CharField(max_length=20, verbose_name="DPI / CUI")
    solicitante_parentesco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Parentesco")
    destino_restos = models.CharField(max_length=200, help_text="Ej: Osario General, Traslado a Guatemala, etc.")
    observaciones_legales = models.TextField(blank=True, null=True)
    responsable_muni = models.CharField(max_length=100, verbose_name="Administrador en Turno")
    archivo_respaldo = models.FileField(upload_to='respaldos_actas/', null=True, blank=True, verbose_name="Documento de Respaldo")

    class Meta:
        verbose_name = "Acta de Exhumación"
        verbose_name_plural = "Libro de Actas de Exhumación"
        ordering = ['-fecha_proceso']

    def __str__(self):
        return f"{self.numero_acta} - {self.nicho.codigo}"

class ReporteDano(models.Model):
    ESTADOS = [('PENDIENTE', '🔴 Pendiente'), ('EN_PROCESO', '🟡 En Proceso'), ('RESUELTO', '🟢 Resuelto')]
    NIVELES = [('LEVE', 'Leve'), ('MODERADO', 'Moderado'), ('CRITICO', 'Crítico')]
    
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='reportes_danos')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    nivel_urgencia = models.CharField(max_length=10, choices=NIVELES, default='LEVE')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    reportado_por = models.CharField(max_length=100, blank=True, null=True)
    
    # Fotos Antes y Después
    foto_evidencia = models.FileField(upload_to='danos/', blank=True, null=True, verbose_name="Foto del Daño (Antes)")
    foto_reparacion = models.FileField(upload_to='reparaciones/', blank=True, null=True, verbose_name="Foto Reparado (Después)")
    
    fecha_solucion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Reparación")
    notas_reparacion = models.TextField(blank=True, null=True, verbose_name="Notas de la Reparación")

    def save(self, *args, **kwargs):
        if self.foto_evidencia:
            self._optimizar_imagen(self.foto_evidencia)
        if self.foto_reparacion:
            self._optimizar_imagen(self.foto_reparacion)
        super().save(*args, **kwargs)

    def _optimizar_imagen(self, campo_archivo):
        try:
            img = Image.open(campo_archivo)
            if img.height > 1200 or img.width > 1200:
                img.thumbnail((1200, 1200))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            temp_buffer = BytesIO()
            img.save(temp_buffer, format='JPEG', quality=75)
            temp_buffer.seek(0)
            nuevo_nombre = os.path.splitext(campo_archivo.name)[0] + ".jpg"
            campo_archivo.save(nuevo_nombre, File(temp_buffer, name=nuevo_nombre), save=False)
        except Exception as e:
            print(f"Error procesando imagen: {e}")

    class Meta:
        verbose_name = "Reporte de Daño"
        verbose_name_plural = "Control de Daños"

# AUDITORÍA
auditlog.register(Nicho, exclude_fields=['qr_code', 'foto_nicho', 'archivo_acta', 'archivo_titulo'])
auditlog.register(ActaExhumacion)
auditlog.register(ReporteDano, exclude_fields=['foto_evidencia', 'foto_reparacion'])
from .models_pagos import PagoArbitrio
