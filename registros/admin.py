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

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    list_display = ('codigo_con_espacio', 'propietario', 'nombre_difunto', 'lat_f', 'lng_f', 'ver_estado', 'alerta_pago', 'ir_al_mapa')
    search_fields = ('codigo', 'propietario', 'nombre_difunto')
    list_filter = (FiltroUbicacion, 'estado_id', 'fecha_vencimiento')

    def codigo_con_espacio(self, obj):
        return format_html('<div style="min-width: 120px; font-weight: bold;">{}</div>', obj.codigo)
    codigo_con_espacio.short_description = "Código"

    def lat_f(self, obj):
        return f"{obj.lat:.6f}" if obj.lat else "-"
    lat_f.short_description = "Lat"

    def lng_f(self, obj):
        return f"{obj.lng:.6f}" if obj.lng else "-"
    lng_f.short_description = "Lng"

    # AQUÍ ESTÁ LA CORRECCIÓN DEL MAPA SATELITAL
    def ir_al_mapa(self, obj):
        if obj.lat and obj.lng:
            # Nueva URL corregida: t=k activa satélite, z=20 es el zoom
            url = f"https://www.google.com/maps/search/?api=1&query={obj.lat},{obj.lng}&t=k&z=20"
            return format_html('<a href="{}" target="_blank" style="background: #2196F3; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">🛰️ Ver Satélite</a>', url)
        return "Sin GPS"
    ir_al_mapa.short_description = "Mapa"

    def ver_estado(self, obj):
        colores = {1: '#4CAF50', 2: '#F44336', 3: '#FF9800'}
        nombres = {1: '✅ DISPONIBLE', 2: '⚰️ OCUPADO', 3: '📝 RESERVADO'}
        color = colores.get(obj.estado_id, '#000')
        nombre = nombres.get(obj.estado_id, 'Estado')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, nombre)
    ver_estado.short_description = "Estado"

    def alerta_pago(self, obj):
        if obj.fecha_vencimiento and obj.fecha_vencimiento < timezone.now().date():
            return format_html('<span style="color: red; font-weight: bold;">🚨 DEUDA</span>')
        return "N/A"
    alerta_pago.short_description = "Finanzas"

@admin.register(FotoCampo)
class FotoCampoAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'miniatura')
    def miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;"/>', obj.imagen.url)
        return "No hay foto"

@admin.register(Exhumacion)
class ExhumacionAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'nombre_difunto_retirado', 'fecha_exhumacion')
