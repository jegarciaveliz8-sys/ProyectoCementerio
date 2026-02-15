import csv
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.utils import timezone
from .models import Nicho, FotoCampo, Exhumacion

class FiltroUbicacion(admin.SimpleListFilter):
    title = "Estado de Ubicación"
    parameter_name = "ubicacion"
    def lookups(self, request, model_admin):
        return (
            ("real", "📍 Solo Reales (Mapeados)"),
            ("reserva", "☁️ Solo Reservas (Amontonados)"),
        )
    def queryset(self, request, queryset):
        if self.value() == "real":
            return queryset.exclude(lat=14.7822)
        if self.value() == "reserva":
            return queryset.filter(lat=14.7822)
        return queryset

class NichoAdminForm(forms.ModelForm):
    class Meta:
        model = Nicho
        fields = '__all__'

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    form = NichoAdminForm
    list_display = ('codigo', 'propietario', 'nombre_difunto', 'lat', 'lng', 'ver_estado', 'alerta_pago', 'ir_al_mapa')
    search_fields = ('codigo', 'propietario', 'nombre_difunto', 'dpi_propietario')
    list_filter = (FiltroUbicacion, 'estado_id', 'fecha_vencimiento')
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
                return format_html('<span style="background: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>', "🚨 DEUDA")
            return format_html('<span style="color: #27ae60; font-weight: bold;">{}</span>', "✅ AL DÍA")
        return format_html('<span style="color: #95a5a6;">{}</span>', "N/A")
    alerta_pago.short_description = "Finanzas"

    def ir_al_mapa(self, obj):
        if obj.lat and obj.lng:
            # Link mejorado: t=k (satélite) y z=20 (zoom máximo)
            url = f"https://www.google.com/maps?q={obj.lat},{obj.lng}&t=k&z=20"
            return format_html('<a href="{}" target="_blank" style="background: #2196F3; color: white; padding: 3px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">📍 Ver Satélite</a>', url)
        return format_html('<span style="color: #ccc;">{}</span>', "Sin GPS")
    ir_al_mapa.short_description = "Mapa"

    def descargar_pdf(self, request, queryset):
        from django.shortcuts import redirect
        if queryset.count() == 1:
            return redirect('generar_titulo_pdf', nicho_id=queryset[0].id)
        self.message_user(request, "⚠️ Seleccione solo un registro.")
    descargar_pdf.short_description = "📄 Generar Título (PDF)"

    def exportar_excel(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="RESPALDO_COORDENADAS.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['Código', 'Dueño', 'Difunto', 'Latitud', 'Longitud', 'Estado', 'Vencimiento'])
        for n in queryset:
            estado = "Disponible" if n.estado_id == 1 else "Ocupado"
            writer.writerow([n.codigo, n.propietario, n.nombre_difunto, n.lat, n.lng, estado, n.fecha_vencimiento])
        return response
    exportar_excel.short_description = "📊 Respaldar datos y coordenadas (Excel)"

@admin.register(FotoCampo)
class FotoCampoAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'miniatura')
    def miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:5px;" />', obj.imagen.url)
        return "Sin foto"

@admin.register(Exhumacion)
class ExhumacionAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'nombre_difunto_retirado', 'fecha_exhumacion', 'imprimir_acta')
    search_fields = ('nombre_difunto_retirado', 'nicho__codigo')
    def imprimir_acta(self, obj):
        return format_html('<a style="background: #2196F3; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" href="/exhumacion/pdf/{}/" target="_blank">📄 Ver Acta</a>', obj.id)
