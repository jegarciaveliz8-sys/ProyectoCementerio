import csv
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.utils import timezone
from .models import Nicho, FotoCampo, Exhumacion

# --- FORMULARIO CON VALIDACIONES ---
class NichoAdminForm(forms.ModelForm):
    class Meta:
        model = Nicho
        fields = '__all__'

    def clean_dpi_propietario(self):
        dpi = self.cleaned_data.get('dpi_propietario')
        if dpi:
            dpi_limpio = dpi.replace(" ", "").replace("-", "")
            if not dpi_limpio.isdigit() or len(dpi_limpio) != 13:
                raise forms.ValidationError("🚨 El DPI debe tener exactamente 13 números.")
            return dpi_limpio
        return dpi

# --- ADMINISTRACIÓN DE NICHOS ---
@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    form = NichoAdminForm
    list_display = ('codigo', 'propietario', 'nombre_difunto', 'ver_estado', 'alerta_pago', 'ir_al_mapa', 'ver_qr')
    search_fields = ('codigo', 'propietario', 'nombre_difunto')
    list_filter = ('estado_id', 'fecha_vencimiento')
    actions = ['descargar_pdf', 'exportar_excel']

    def ver_estado(self, obj):
        colores = {1: '#4CAF50', 2: '#F44336', 3: '#FF9800'}
        nombres = {1: '✅ DISPONIBLE', 2: '⚰️ OCUPADO', 3: '📝 RESERVADO'}
        color = colores.get(obj.estado_id, '#000')
        nombre = nombres.get(obj.estado_id, 'DESCONOCIDO')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, nombre)
    ver_estado.short_description = "Estado"

    def alerta_pago(self, obj):
        if obj.fecha_vencimiento:
            if obj.fecha_vencimiento < timezone.now().date():
                return format_html('<span style="background: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">🚨 DEUDA</span>')
            return format_html('<span style="color: #27ae60; font-weight: bold;">✅ AL DÍA</span>')
        return format_html('<span style="color: #95a5a6;">N/A</span>')
    alerta_pago.short_description = "Finanzas"

    # CORRECCIÓN AQUÍ: Cambié latitud/longitud por lat/lng
    def ir_al_mapa(self, obj):
        if obj.lat and obj.lng:
            return format_html('<a href="/mapa/?id={}" target="_blank" style="color: #2196F3; font-weight: bold;">📍 Ver Satélite</a>', obj.id)
        return format_html('<span style="color: #ccc;">Sin GPS</span>')
    ir_al_mapa.short_description = "Mapa"

    def ver_qr(self, obj):
        datos = f"Nicho:{obj.codigo}|DPI:{obj.dpi_propietario}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={datos}"
        return format_html('<a href="{}" target="_blank">📲 QR</a>', qr_url)
    ver_qr.short_description = "QR"

    def has_delete_permission(self, request, obj=None): return False

    def descargar_pdf(self, request, queryset):
        from django.shortcuts import redirect
        if queryset.count() == 1:
            return redirect('generar_titulo_pdf', nicho_id=queryset[0].id)
        self.message_user(request, "⚠️ Seleccione solo un registro.")
    descargar_pdf.short_description = "📄 Generar Título (PDF)"

    def exportar_excel(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_cementerio.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['Código', 'Dueño Legal', 'Difunto', 'Estado', 'Vencimiento'])
        for n in queryset:
            estado = "Disponible" if n.estado_id == 1 else "Ocupado"
            writer.writerow([n.codigo, n.propietario, n.nombre_difunto, estado, n.fecha_vencimiento])
        return response
    exportar_excel.short_description = "📊 Exportar Excel"

@admin.register(FotoCampo)
class FotoCampoAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'miniatura')
    def miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:5px; border:1px solid #ddd;" />', obj.imagen.url)
        return "Sin foto"
    miniatura.short_description = "Vista Previa"

@admin.register(Exhumacion)
class ExhumacionAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'nombre_difunto_retirado', 'fecha_exhumacion', 'imprimir_acta')
    list_filter = ('fecha_exhumacion',)
    search_fields = ('nombre_difunto_retirado', 'nicho__codigo')
    def has_delete_permission(self, request, obj=None): return False
    def imprimir_acta(self, obj):
        return format_html('<a style="background: #2196F3; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;" href="/exhumacion/pdf/{}/" target="_blank">📄 Ver Acta</a>', obj.id)
    imprimir_acta.short_description = "Generar Acta"
