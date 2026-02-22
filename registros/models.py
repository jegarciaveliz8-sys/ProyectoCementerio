from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from PIL import Image

class Nicho(models.Model):
    history = HistoricalRecords()
    codigo = models.CharField(max_length=50, unique=True)
    lat = models.FloatField()
    lng = models.FloatField()
    nombre_difunto = models.TextField(blank=True, null=True, verbose_name="Nombres de Difuntos")
    estado_id = models.BigIntegerField(default=1)
    propietario = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dueño Legal")
    dpi_propietario = models.CharField(max_length=15, blank=True, null=True, verbose_name="DPI")
    numero_titulo = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. de Título/Escritura")
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Notas de Propiedad")
    foto = models.ImageField(upload_to='nichos/', blank=True, null=True, verbose_name='Foto del Nicho')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, editable=False)
    fecha_pago = models.DateField(blank=True, null=True, verbose_name='Fecha de Último Pago')
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    monto_arbitrio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Monto de Arbitrio (Q)')

    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    def save(self, *args, **kwargs):
        # Generar QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        url_publica = f"http://192.168.1.39:8050/nicho/{self.codigo}/"
        qr.add_data(url_publica)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        fname = f'qr-{self.codigo}.png'
        buffer = BytesIO()
        qr_image.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        qr_image.close()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.propietario if self.propietario else 'Sin Dueño'}"

class FotoCampo(models.Model):
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='inspecciones/%Y/%m/%d/')
    fecha_toma = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Fotos de Campo"

    def __str__(self):
        return f"Foto de {self.nicho.codigo} - {self.fecha_toma.strftime('%d/%m/%Y')}"

class Exhumacion(models.Model):
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='exhumaciones', verbose_name="Nicho Relacionado")
    fecha_exhumacion = models.DateField(verbose_name="Fecha de la Exhumación")
    nombre_difunto_retirado = models.CharField(max_length=200, verbose_name="Nombre del Difunto Retirado")
    solicitante = models.CharField(max_length=200, verbose_name="Familiar que solicita / Autoridad")
    documento_autorizacion = models.CharField(max_length=100, blank=True, null=True, verbose_name="No. de Oficio o Acta")
    destino_restos = models.CharField(max_length=255, verbose_name="Destino de los restos (Osario/Otro)")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Notas del Proceso")

    class Meta:
        verbose_name = "Exhumación"
        verbose_name_plural = "Exhumaciones"

    def __str__(self):
        return f"Exhumación {self.nicho.codigo} - {self.fecha_exhumacion}"

@receiver(post_save, sender=Exhumacion)
def limpiar_nicho_tras_exhumacion(sender, instance, created, **kwargs):
    if created:
        nicho = instance.nicho
        nicho.estado_id = 1
        nicho.nombre_difunto = ""
        nicho.save()
