from django.contrib import admin
from .models import Nicho
from django.utils.html import format_html

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    # LA LISTA: Rápida y con alertas
    list_display = ('codigo', 'estado_legal', 'pago_status', 'ver_mapa', 'boton_imprimir')
    search_fields = ('codigo', 'nombre_difunto')
    
    # ORGANIZACIÓN DEL FORMULARIO POR PESTAÑAS (Fieldsets)
    fieldsets = (
        ('📋 DATOS BÁSICOS', {
            'fields': ('codigo', 'propietario', 'nombre_difunto')
        }),
        ('💰 FINANZAS Y UBICACIÓN', {
            'fields': (('monto_arbitrio', 'fecha_vencimiento'), ('lat', 'lng'))
        }),
        ('⚖️ EXPEDIENTE LEGAL / EXHUMACIONES', {
            'classes': ('collapse',), # Esto lo mantiene oculto hasta que le das clic
            'fields': ('esta_exhumado', 'acta_exhumacion', 'foto_nicho', 'notas_legales'),
        }),
    )

    # --- FUNCIONES DE ESTADO ---
    def estado_legal(self, obj):
        if obj.esta_exhumado:
            return format_html('<span style="background:#000; color:#fff; padding:3px 8px; border-radius:10px;">💀 EXHUMADO</span>')
        return format_html('<span style="color:#2980b9;">👤 OCUPADO</span>')
    estado_legal.short_description = "ESTADO LEGAL"

    def pago_status(self, obj):
        color = "#2ecc71" if obj.monto_arbitrio > 0 else "#e74c3c"
        return format_html('<b style="color:{};">Q{}</b>', color, obj.monto_arbitrio)

    def ver_mapa(self, obj):
        if obj.lat and obj.lng:
            return format_html('<a href="/?nicho={}" target="_blank">📍 VER</a>', obj.codigo)
        return "-"

    def boton_imprimir(self, obj):
        return format_html('<a href="/imprimir/{}/" target="_blank" style="background:#444; color:white; padding:3px 8px; border-radius:3px; text-decoration:none;">🖨️ FICHA</a>', obj.id)

