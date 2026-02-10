from django.db import models

class Nicho(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    lat = models.FloatField()
    lng = models.FloatField()
    nombre_difunto = models.TextField(blank=True, null=True, verbose_name="Nombres de Difuntos")
    estado_id = models.BigIntegerField(default=1)
    
    # --- NUEVOS CAMPOS FASE DE PROPIEDAD ---
    propietario = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dueño Legal")
    dpi_propietario = models.CharField(max_length=15, blank=True, null=True, verbose_name="DPI")
    numero_titulo = models.CharField(max_length=50, blank=True, null=True, verbose_name="No. de Título/Escritura")
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Notas de Propiedad")
    foto = models.ImageField(upload_to='nichos/', blank=True, null=True, verbose_name='Foto del Nicho')
    fecha_pago = models.DateField(blank=True, null=True, verbose_name='Fecha de Último Pago')
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    monto_arbitrio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Monto de Arbitrio (Q)')

    def __str__(self):
        return f"{self.codigo} - {self.propietario if self.propietario else 'Sin Dueño'}"

class FotoCampo(models.Model):
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='inspecciones/%Y/%m/%d/')
    fecha_toma = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Foto de Campo"
        verbose_name = "Fotos de Campo"

    def __str__(self):
        return f"Foto de {self.nicho.codigo} - {self.fecha_toma.strftime('%d/%m/%Y')}"
