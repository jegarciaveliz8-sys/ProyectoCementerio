import urllib.parse
import os
import csv
from django.contrib import admin
from django.db.models import Count, Q, Sum
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.conf import settings
from datetime import date

# Librerías de Importación
from .models import Nicho, ReporteDano, ActaExhumacion
from .models_pagos import PagoArbitrio
from import_export.admin import ImportExportModelAdmin

# --- HISTORIAL DE PAGOS (INLINE - INTOCABLE) ---
class PagoArbitrioInline(admin.TabularInline):
    model = PagoArbitrio
    extra = 1
    fields = ('fecha_pago', 'numero_recibo', 'monto_pagado', 'observaciones')

# --- LIBRO DE ACTAS PROFESIONAL (NUEVO INLINE) ---
class ActaExhumacionInline(admin.StackedInline):
    model = ActaExhumacion
    extra = 1
    verbose_name = "Registro de Exhumación (Libro de Actas)"
    verbose_name_plural = "Historial de Exhumaciones en este Nicho"
    classes = ('collapse',)
    fieldsets = (
        ('Datos de Control', {'fields': ('numero_acta', 'tipo', 'fecha_proceso', 'responsable_muni')}),
        ('Solicitante', {'fields': ('solicitante_nombre', 'solicitante_dpi', 'solicitante_parentesco')}),
        ('Destino', {'fields': ('destino_restos', 'observaciones_legales')}),
    )

# --- FILTROS (MANTENIENDO TU LÓGICA EXACTA) ---
class MoraConTituloFilter(admin.SimpleListFilter):
    title = 'Prioridad de Cobro'
    parameter_name = 'prioridad_cobro'
    def lookups(self, request, model_admin):
        return (('urgente', '🔴 Con Título y Mora'), ('limpio', '🟢 Solventes con Título'))
    def queryset(self, request, queryset):
        if self.value() == 'urgente':
            return queryset.exclude(numero_titulo__isnull=True).exclude(numero_titulo='').filter(monto_arbitrio__gt=0)
        if self.value() == 'limpio':
            return queryset.exclude(numero_titulo__isnull=True).exclude(numero_titulo='').filter(monto_arbitrio=0)

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
    
    # IMPORTANTE: Aquí activamos ambos inlines
    inlines = [PagoArbitrioInline, ActaExhumacionInline]
    
    list_display = (
        'codigo', 'foto_miniatura', 'nombre_difunto_corto', 
        'numero_titulo', 'lat', 'lng', 'monto_arbitrio', 
        'estado_mora', 'ver_mapa_link', 
        'boton_titulo', 'boton_solvencia', 'boton_cobro', 
        'boton_acta', 'boton_gps'
    )
    
    list_editable = ('numero_titulo', 'lat', 'lng', 'monto_arbitrio')
    list_filter = (MoraConTituloFilter, GPSFilter, DocumentacionFilter, 'esta_exhumado', ('fecha_vencimiento', admin.DateFieldListFilter))
    search_fields = ('codigo', 'nombre_difunto', 'propietario')

    actions = ['exportar_lista_cobro']

    @admin.action(description="📦 Descargar Listado para Notificadores (Excel/CSV)")
    def exportar_lista_cobro(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="cobros_sanarate_{date.today()}.csv"'
        writer = csv.writer(response)
        writer.writerow(['CODIGO', 'PROPIETARIO', 'DIFUNTO', 'MONTO PENDIENTE', 'ESTADO'])
        for n in queryset:
            writer.writerow([n.codigo, n.propietario, n.nombre_difunto, n.monto_arbitrio, n.semaforo_estado['estado']])
        return response

    def boton_acta(self, obj):
        if obj.esta_exhumado:
            html = f"""
            <div class="acta-wrapper" style="position:relative; display:inline-block;">
                <button type="button" style="background:#475569; color:white; padding:4px 6px; border-radius:4px; border:none; font-weight:bold; font-size:9px; cursor:pointer;">
                   🦴 ACTA ▾
                </button>
                <div class="acta-menu" style="display:none; position:absolute; right:0; background:white; min-width:140px; box-shadow:0 4px 12px rgba(0,0,0,0.15); z-index:9999; border-radius:4px; overflow:hidden; border:1px solid #ddd;">
                    <a href="/nicho/{obj.id}/acta-exhumacion/?tipo=ADMINISTRATIVA" target="_blank" style="display:block; padding:8px; color:#334155; text-decoration:none; font-size:10px; border-bottom:1px solid #eee;">🏛️ Municipal</a>
                    <a href="/nicho/{obj.id}/acta-exhumacion/?tipo=JUDICIAL" target="_blank" style="display:block; padding:8px; color:#b91c1c; text-decoration:none; font-size:10px; border-bottom:1px solid #eee;">⚖️ Judicial</a>
                    <a href="/nicho/{obj.id}/acta-exhumacion/?tipo=FAMILIAR" target="_blank" style="display:block; padding:8px; color:#15803d; text-decoration:none; font-size:10px; border-bottom:1px solid #eee;">👨‍👩‍👦 Familiar</a>
                    <a href="/nicho/{obj.id}/acta-exhumacion/?tipo=SANITARIA" target="_blank" style="display:block; padding:8px; color:#d97706; text-decoration:none; font-size:10px;">☣️ Sanitaria</a>
                </div>
            </div>
            <script>
                document.querySelectorAll('.acta-wrapper').forEach(w => {{
                    w.onmouseover = () => w.querySelector('.acta-menu').style.display = 'block';
                    w.onmouseout = () => w.querySelector('.acta-menu').style.display = 'none';
                }});
            </script>
            """
            return mark_safe(html)
        return mark_safe('<span style="color:#cbd5e1;font-size:9px;">-</span>')
    boton_acta.short_description = "EXPEDIENTE"

    def boton_cobro(self, obj):
        url = f"/nicho/{obj.id}/aviso-mora/"
        return format_html('<a href="{}" target="_blank" style="background:#dc2626;color:white;padding:4px 6px;border-radius:4px;text-decoration:none;font-weight:bold;font-size:9px;">🚫 COBRO</a>', url)
    boton_cobro.short_description = "ACCION"

    def boton_titulo(self, obj):
        url = f"/nicho/{obj.id}/titulo/"
        return format_html('<a href="{}" target="_blank" style="background:#1e293b;color:white;padding:4px 6px;border-radius:4px;text-decoration:none;font-weight:bold;font-size:9px;">📜 TÍTULO</a>', url)
    boton_titulo.short_description = "PROPIEDAD"

    def boton_solvencia(self, obj):
        url = f"/nicho/{obj.id}/solvencia/"
        return format_html('<a href="{}" target="_blank" style="background:#0369a1;color:white;padding:4px 6px;border-radius:4px;text-decoration:none;font-weight:bold;font-size:9px;">📑 SOLVENCIA</a>', url)
    boton_solvencia.short_description = "ESTADO"

    def ver_mapa_link(self, obj):
        if obj.lat and obj.lng:
            url = f"https://www.google.com/maps?q={obj.lat},{obj.lng}"
            return format_html('<a href="{}" target="_blank" style="background:#ea4335;color:white;padding:4px 6px;border-radius:4px;text-decoration:none;font-size:9px;font-weight:bold;">📍 VER</a>', url)
        return mark_safe('<span style="color:#94a3b8;font-size:9px;">Sin GPS</span>')

    def foto_miniatura(self, obj):
        if obj.foto_nicho:
            return format_html('<img src="{}" style="width:35px;height:35px;border-radius:4px;object-fit:cover;"/>', obj.foto_nicho.url)
        return mark_safe('<span style="color:#94a3b8;font-size:9px;">📷 No</span>')

    def estado_mora(self, obj):
        res = obj.semaforo_estado
        return format_html('<span style="background:{}; color:white; padding:3px 6px; border-radius:4px; font-size:10px; font-weight:bold; display:block; text-align:center;">{}</span>', res['color'], res['estado'])

    def nombre_difunto_corto(self, obj):
        nombre = obj.nombre_difunto or "DISPONIBLE"
        return nombre[:18] + ".." if len(nombre) > 18 else nombre

    def boton_gps(self, obj):
        js = "navigator.geolocation.getCurrentPosition(function(p){ var r=document.activeElement.closest('tr'); r.querySelector('.field-lat input').value=p.coords.latitude.toFixed(8); r.querySelector('.field-lng input').value=p.coords.longitude.toFixed(8); r.style.background='#fff3cd'; });"
        return mark_safe(f'<button type="button" onclick="{js}" style="background:#4285f4;color:white;border:none;padding:5px 8px;border-radius:4px;font-size:9px;cursor:pointer;font-weight:bold;">🛰️ GPS</button>')

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        stats = Nicho.objects.aggregate(mapeados=Count('id', filter=Q(lat__gt=0)), total=Count('id'))
        total_mora = qs.aggregate(Sum('monto_arbitrio'))['monto_arbitrio__sum'] or 0.00
        header = f"""
        <div style="background:#1e293b;color:white;padding:15px;border-radius:10px;margin-bottom:15px;display:flex;justify-content:space-between;align-items:center;border-left:8px solid #3b82f6;">
            <div><b style="font-size:18px;">CATASTRO MUNICIPAL - SANARATE</b></div>
            <div style="display:flex; gap:10px;">
                <div style="background:#0f172a;padding:8px 15px;border-radius:8px;">
                    <small>TOTAL EN MORA (FILTRADO):</small> <b style="color:#f87171;">Q {total_mora:,.2f}</b>
                </div>
                <div style="background:#0f172a;padding:8px 15px;border-radius:8px;">
                    <small>MAPEO:</small> <b>{stats['mapeados']} / {stats['total']}</b>
                </div>
            </div>
        </div>
        """
        response.context_data['title'] = mark_safe(header)
        return response

admin.site.register(ReporteDano)
admin.site.register(ActaExhumacion)
