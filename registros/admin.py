import urllib.parse
from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Nicho, ReporteDano
from import_export.admin import ImportExportModelAdmin

class DocumentacionFilter(admin.SimpleListFilter):
    title = 'Estado de Expediente'
    parameter_name = 'expediente'
    def lookups(self, request, model_admin):
        return (('completo', '✅ Todo Completo'), ('sin_titulo', '❌ Falta No. Título'), ('con_acta', '🦴 Con Acta Exhumación'))
    def queryset(self, request, queryset):
        if self.value() == 'completo': return queryset.exclude(numero_titulo__isnull=True).exclude(numero_titulo='')
        if self.value() == 'sin_titulo': return queryset.filter(Q(numero_titulo__isnull=True) | Q(numero_titulo=''))
        if self.value() == 'con_acta': return queryset.exclude(numero_acta__isnull=True).exclude(numero_acta='')

class GPSFilter(admin.SimpleListFilter):
    title = 'Estado de Mapeo'
    parameter_name = 'tiene_gps'
    def lookups(self, request, model_admin):
        return (('si', '✅ Con Coordenadas'), ('no', '❌ Pendientes de GPS'),)
    def queryset(self, request, queryset):
        if self.value() == 'si': return queryset.filter(lat__gt=0)
        if self.value() == 'no': return queryset.filter(Q(lat__isnull=True) | Q(lat=0))

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin):
    list_per_page = 50
    ordering = ('codigo',)
    
    list_display = (
        'codigo', 'foto_miniatura', 'nombre_difunto_corto', 
        'numero_titulo', 'lat', 'lng', 'estado_mora', 
        'ver_mapa_link', 'boton_gps', 'auditoria'
    )
    
    list_editable = ('lat', 'lng', 'numero_titulo')
    list_filter = (GPSFilter, DocumentacionFilter, 'esta_exhumado', ('fecha_vencimiento', admin.DateFieldListFilter))
    search_fields = ('codigo', 'nombre_difunto', 'lat', 'lng')

    def ver_mapa_link(self, obj):
        if obj.lat and obj.lng:
            # FORMATO DE ENLACE UNIVERSAL DE GOOGLE MAPS
            url = f"https://www.google.com/maps/search/?api=1&query={obj.lat},{obj.lng}"
            return format_html('<a href="{}" target="_blank" style="background:#ea4335;color:white;padding:5px 10px;border-radius:5px;text-decoration:none;font-size:11px;font-weight:bold;box-shadow: 1px 1px 3px rgba(0,0,0,0.2);">📍 VER EN MAPA</a>', url)
        return mark_safe('<span style="color:#94a3b8;font-size:10px;">Sin GPS</span>')
    ver_mapa_link.short_description = "GOOGLE MAPS"

    def foto_miniatura(self, obj):
        if obj.foto_nicho:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:5px;object-fit:cover;"/>', obj.foto_nicho.url)
        return mark_safe('<span style="color:#94a3b8;font-size:9px;">📷 No</span>')
    foto_miniatura.short_description = "FOTO"

    def estado_mora(self, obj):
        res = obj.semaforo_estado
        return format_html('<span style="background:{}; color:white; padding:3px 6px; border-radius:4px; font-size:10px; font-weight:bold; display:block; text-align:center;">{}</span>', res['color'], res['estado'])
    estado_mora.short_description = "MORA"

    def nombre_difunto_corto(self, obj):
        nombre = obj.nombre_difunto or "DISPONIBLE"
        return nombre[:18] + ".." if len(nombre) > 18 else nombre
    nombre_difunto_corto.short_description = "DIFUNTO"

    def boton_gps(self, obj):
        js = "navigator.geolocation.getCurrentPosition(function(p){ var r=document.activeElement.closest('tr'); r.querySelector('.field-lat input').value=p.coords.latitude.toFixed(8); r.querySelector('.field-lng input').value=p.coords.longitude.toFixed(8); r.style.background='#fff3cd'; });"
        return mark_safe(f'<button type="button" onclick="{js}" style="background:#4285f4;color:white;border:none;padding:5px 8px;border-radius:4px;font-size:11px;cursor:pointer;font-weight:bold;">🛰️ CAPTURAR</button>')

    def auditoria(self, obj):
        return format_html('<a href="/admin/admin_tools/logentry/?object_id={}" style="font-size:10px;color:#3b82f6;">Log</a>', obj.id)
    auditoria.short_description = "HIST."

    def changelist_view(self, request, extra_context=None):
        stats = Nicho.objects.aggregate(mapeados=Count('id', filter=Q(lat__gt=0)), total=Count('id'))
        header = f"""
        <div style="background:#1e293b;color:white;padding:15px;border-radius:10px;margin-bottom:15px;display:flex;justify-content:space-between;align-items:center;border-left:8px solid #3b82f6;">
            <div><b style="font-size:18px;">CATASTRO MUNICIPAL - SANARATE</b></div>
            <div style="background:#0f172a;padding:8px 15px;border-radius:8px;">
                <small>MAPEO:</small> <b>{stats['mapeados']} / {stats['total']}</b>
            </div>
        </div>
        """
        extra_context = extra_context or {}
        extra_context['title'] = mark_safe(header)
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(ReporteDano)
