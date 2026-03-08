from django.db import models
from .models import Nicho

class PagoArbitrio(models.Model):
    nicho = models.ForeignKey(Nicho, on_delete=models.CASCADE, related_name='pagos_historial')
    fecha_pago = models.DateField(verbose_name="Fecha de Pago")
    numero_recibo = models.CharField(max_length=50, verbose_name="No. Recibo Municipal")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Q.")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historial de Pago"
        verbose_name_plural = "Historial de Pagos"

    def __str__(self):
        return f"{self.nicho.codigo} - Recibo: {self.numero_recibo}"
