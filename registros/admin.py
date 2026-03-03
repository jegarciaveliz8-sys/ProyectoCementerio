import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Nicho
from django.utils.html import format_html

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ver_qr', 'estado_legal', 'pago_status', 'ver_mapa', 'boton_imprimir')
    search_fields = ('codigo', 'nombre_difunto', 'propietario')
    list_filter = ('esta_exhumado', 'monto_arbitrio', 'fecha_vencimiento')
    ordering = ('codigo',)
    
    # 1. Agregamos 'limpiar_pagos' a la lista de acciones
    actions = ['marcar_exhumado', 'marcar_ocupado', 'exportar_a_csv', 'limpiar_pagos']

    # --- NUEVA ACCIÓN: LIMPIAR PAGOS ---
    @admin.action(description="💰 Limpiar saldos (Poner en Q0.00)")
    def limpiar_pagos(self, request, queryset):
        filas_actualizadas = queryset.update(monto_arbitrio=0.00)
        self.message_user(request, f"Se han reseteado los pagos de {filas_actualizadas} nichos.")

    # --- OTRAS ACCIONES ---
    @admin.action(description="📊 Exportar seleccionados a Excel (CSV)")
    def exportar_a_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_sanarate.csv"'
        writer = csv.writer(response)
        writer.writerow(['Codigo', 'Propietario', 'Difunto', 'Monto', 'Vencimiento', 'Exhumado'])
        for n in queryset:
            writer.writerow([n.codigo, n.propietario, n.nombre_difunto, n.monto_arbitrio, n.fecha_vencimiento, n.esta_exhumado])
        return response

    @admin.action(description="💀 Marcar como EXHUMADOS")
    def marcar_exhumado(self, request, queryset):
        queryset.update(esta_exhumado=True)

    @admin.action(description="👤 Marcar como OCUPADOS")
    def marcar_ocupado(self, request, queryset):
        queryset.update(esta_exhumado=False)

    # --- FUNCIONES DE COLUMNAS (IGUAL QUE ANTES) ---
    def ver_qr(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="width:30px; height:30px; border:1px solid #eee;"/>', obj.qr_code.url)
        return "-"
    ver_qr.short_description = "QR"

    def estado_legal(self, obj):
        if obj.esta_exhumado:
            return format_html('<span style="background:#000; color:#fff; padding:2px 8px; border-radius:10px; font-size:11px;">💀 EXHUMADO</span>')
        return format_html('<span style="color:#2980b9; font-weight:bold;">👤 OCUPADO</span>')
    estado_legal.short_description = "ESTADO"

    def pago_status(self, obj):
        color = "#2ecc71" if obj.monto_arbitrio > 0 else "#e74c3c"
        return format_html('<b style="color:{};">Q{}</b>', color, obj.monto_arbitrio)
    pago_status.short_description = "PAGO"

    def ver_mapa(self, obj):
        if obj.lat and obj.lng:
            return format_html('<a href="/?nicho={}" style="text-decoration:none;">📍 VER</a>', obj.codigo)
        return "-"
    ver_mapa.short_description = "MAPA"

    def boton_imprimir(self, obj):
        return format_html(
            '<a href="/imprimir/{}/" target="_blank" style="background:#444; color:white; padding:3px 10px; border-radius:4px; text-decoration:none; font-size:11px;">FICHA</a>', 
            obj.id
        )
    boton_imprimir.short_description = "IMPRIMIR"
