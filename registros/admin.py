from django.contrib import admin
from django.utils.html import format_html
from .models import Nicho, FotoCampo, Exhumacion

class FiltroUbicacion(admin.SimpleListFilter):
    title = "Estado de Ubicación"
    parameter_name = "ubicacion"
    def lookups(self, request, model_admin):
        return (("real", "📍 Solo Mapeados"), ("reserva", "☁️ Solo Reservas"))
    def queryset(self, request, queryset):
        if self.value() == "real": return queryset.exclude(lat__icontains="14,781402")
        if self.value() == "reserva": return queryset.filter(lat__icontains="14,781402")
        return queryset

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    # 'antorcha' es la columna con el ícono rojo
    list_display = ('antorcha', 'codigo', 'lat', 'lng', 'ver_estado')
    list_filter = (FiltroUbicacion, 'estado_id', 'fecha_vencimiento')
    search_fields = ('codigo', 'propietario')

    def antorcha(self, obj):
        if obj.lat and obj.lng:
            # LIMPIEZA: Cambiamos comas por puntos y quitamos espacios
            la = str(obj.lat).replace(',', '.').strip()
            lo = str(obj.lng).replace(',', '.').strip()
            
            # NUEVA URL: Esta es la que obliga a Google a poner la marca roja
            # 'query' le dice a Google: "Busca esto y ponle un pin"
            # '&basemap=satellite' intenta abrir la vista satelital directo
            url = f"https://www.google.com/maps/search/?api=1&query={la},{lo}"
            
            return format_html(
                '<a href="{}" target="_blank" title="Ubicar Nicho" style="font-size: 22px; text-decoration: none;">'
                '📍'
                '</a>', url
            )
        return "⚪"
    antorcha.short_description = "Ubicación"

    def ver_estado(self, obj):
        color = {1: '#4CAF50', 2: '#F44336', 3: '#FF9800'}.get(obj.estado_id, '#000')
        nombre = {1: '✅ DISPONIBLE', 2: '⚰️ OCUPADO', 3: '📝 RESERVADO'}.get(obj.estado_id, '...')
        return format_html('<b style="color: {};">{}</b>', color, nombre)
    ver_estado.short_description = "Estado"

admin.site.register(FotoCampo)
admin.site.register(Exhumacion)
