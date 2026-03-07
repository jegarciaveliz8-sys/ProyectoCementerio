import urllib.parse
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.utils.safestring import mark_safe
from .models import Nicho, ReporteDano
from import_export.admin import ImportExportModelAdmin
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin):
    list_per_page = 50
    ordering = ('codigo',)
    
    # Agregamos 'historial' para ver quién tocó el registro
    list_display = (
        'codigo', 'ver_qr', 'ver_foto', 'nombre_difunto', 
        'lat', 'lng', 'boton_gps', 'monto_arbitrio', 'accion_cobro', 'ver_logs'
    )
    
    list_editable = ('lat', 'lng', 'monto_arbitrio')
    readonly_fields = ('ver_foto_grande', 'ver_qr_grande')
    search_fields = ('codigo', 'nombre_difunto', 'propietario')

    # --- FUNCIONES DE NICHO ---
    def ver_qr(self, obj):
        if obj.qr_code: return format_html('<img src="{}" style="width:40px;height:40px;" />', obj.qr_code.url)
        return "-"

    def ver_foto(self, obj):
        if obj.foto_nicho: return format_html('<img src="{}" style="width:40px;height:40px;border-radius:5px;object-fit:cover;" />', obj.foto_nicho.url)
        return mark_safe('<div style="width:40px;height:40px;background:#f1f5f9;border:1px dashed #ccc;border-radius:5px;"></div>')

    def boton_gps(self, obj):
        js = f"navigator.geolocation.getCurrentPosition(function(p){{ var r=document.activeElement.closest('tr'); r.querySelector('.field-lat input').value=p.coords.latitude.toFixed(8); r.querySelector('.field-lng input').value=p.coords.longitude.toFixed(8); }});"
        return mark_safe(f'<button type="button" onclick="{js}" style="background:#0f172a;color:white;border:none;padding:4px 8px;border-radius:4px;font-size:10px;cursor:pointer;">GPS</button>')

    def accion_cobro(self, obj):
        if obj.monto_arbitrio > 0:
            msg = urllib.parse.quote(f"Muni Sanarate: Deuda Q{obj.monto_arbitrio} nicho {obj.codigo}.")
            return format_html('<a href="https://wa.me/?text={}" target="_blank" style="color:#16a34a;font-weight:bold;">📲 WA</a>', msg)
        return "-"

    def ver_logs(self, obj):
        # Link directo al historial de este nicho específico
        ct = ContentType.objects.get_for_model(obj)
        url = f"/admin/auditlog/logentry/?object_id={obj.pk}&content_type={ct.pk}"
        return format_html('<a href="{}" style="font-size:10px;color:#64748b;">🕒 Ver Cambios</a>', url)
    ver_logs.short_description = "AUDITORÍA"

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        stats = qs.aggregate(mora=Sum('monto_arbitrio'), total=Count('id'), mapeados=Count('id', filter=Q(lat__gt=0)))
        extra_context = extra_context or {}
        header = f'<div style="background:#0f172a;color:white;padding:15px;border-radius:10px;margin-bottom:15px;display:flex;justify-content:space-between;"><b>💰 MORA: Q{stats["mora"] or 0:,.2f}</b> <b>📍 GPS: {stats["mapeados"]}/{stats["total"]}</b></div>'
        extra_context['title'] = mark_safe(header)
        return super().changelist_view(request, extra_context=extra_context)

    # --- PREVIEWS ---
    def ver_foto_grande(self, obj):
        if obj.foto_nicho: return format_html('<img src="{}" style="max-width:400px;border-radius:10px;" />', obj.foto_nicho.url)
        return "Sin foto"
    def ver_qr_grande(self, obj):
        if obj.qr_code: return format_html('<img src="{}" style="width:200px;" />', obj.qr_code.url)
        return "No generado"

@admin.register(ReporteDano)
class ReporteDanoAdmin(admin.ModelAdmin):
    list_display = ('nicho_link', 'ver_evidencia', 'urgencia_badge', 'estado_badge', 'reportado_por')
    list_filter = ('estado', 'nivel_urgencia')
    readonly_fields = ('ver_foto_full',)

    def nicho_link(self, obj): return format_html('<b>{}</b>', obj.nicho.codigo)
    
    def ver_evidencia(self, obj):
        if obj.foto_evidencia: return format_html('<img src="{}" style="width:60px;height:60px;object-fit:cover;border:2px solid #ef4444;border-radius:4px;" />', obj.foto_evidencia.url)
        return "Sin foto"

    def urgencia_badge(self, obj):
        color = {'LEVE':'#22c55e', 'MODERADO':'#eab308', 'CRITICO':'#ef4444'}.get(obj.nivel_urgencia, '#ccc')
        return mark_safe(f'<b style="color:white;background:{color};padding:3px 8px;border-radius:10px;font-size:10px;">{obj.nivel_urgencia}</b>')

    def estado_badge(self, obj):
        color = {'PENDIENTE':'#ef4444', 'EN_PROCESO':'#3b82f6', 'RESUELTO':'#22c55e'}.get(obj.estado, '#ccc')
        return mark_safe(f'<b style="color:{color};border:1px solid {color};padding:2px 5px;border-radius:4px;font-size:10px;">{obj.get_estado_display()}</b>')

    def ver_foto_full(self, obj):
        if obj.foto_evidencia: return format_html('<img src="{}" style="max-width:500px;border-radius:10px;" />', obj.foto_evidencia.url)
        return "No hay evidencia"
