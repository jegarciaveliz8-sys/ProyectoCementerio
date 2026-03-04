import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Nicho
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.utils import timezone

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_difunto', 'propietario', 'status_financiero', 'indicador_tiempo', 'consola_tecnologica')
    list_editable = ('nombre_difunto', 'propietario')
    search_fields = ('codigo', 'nombre_difunto', 'propietario')
    ordering = ('id',)
    
    list_filter = (
        'esta_exhumado', 
        'monto_arbitrio', 
        ('fecha_vencimiento', admin.DateFieldListFilter),
        'fecha_pago'
    )
    
    actions = ['exportar_a_csv', 'marcar_exhumado_masivo']

    def status_financiero(self, obj):
        if obj.monto_arbitrio > 0:
            return format_html('<b style="color:#28a745;">✅ Q{}</b>', obj.monto_arbitrio)
        return mark_safe('<b style="color:#dc3545;">🚨 MORA</b>')
    status_financiero.short_description = "Finanzas"

    def indicador_tiempo(self, obj):
        if not obj.fecha_vencimiento: 
            return mark_safe('<span style="color:#f39c12;">SIN FECHA</span>')
        dias = (obj.fecha_vencimiento - timezone.now().date()).days
        color = "#28a745" if dias > 0 else "#dc3545"
        return format_html('<b style="color:{};">{} días</b>', color, dias)
    indicador_tiempo.short_description = "Vencimiento"

    # 🛰️ AQUÍ ESTÁ LA MEJORA DEL RADAR
    def consola_tecnologica(self, obj):
        links = []
        links.append(format_html('<a href="/imprimir/{}/" target="_blank" title="Ficha" style="text-decoration:none; font-size:18px;">📄</a>', obj.id))
        
        if obj.lat and obj.lng:
            # Mandamos coordenadas + zoom nivel 20 + código para el radar
            links.append(format_html(
                '<a href="/mapa/?lat={}&lng={}&z=20&codigo={}&zoom=true" '
                'title="Ubicar en Radar" '
                'style="text-decoration:none; margin-left:10px; font-size:18px;">📍</a>', 
                obj.lat, obj.lng, obj.codigo
            ))
        return mark_safe(f'<div style="display:flex; align-items:center; justify-content:center;">{" ".join(links)}</div>')
    consola_tecnologica.short_description = "Acciones G.I.S."

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request).aggregate(
            p=Sum('monto_arbitrio'), 
            m=Count('id', filter=Q(monto_arbitrio=0)), 
            t=Count('id')
        )
        extra_context = extra_context or {}
        extra_context['title'] = format_html(
            '<div style="background:#111827; padding:20px; border-radius:12px; color:white; display:flex; gap:50px; border-bottom:5px solid #374151; margin-bottom:20px;">'
            '<div><small style="color:#9ca3af; font-weight:bold;">💰 RECAUDACIÓN</small><br><span style="font-size:24px; font-weight:bold; color:#4ade80;">Q{}</span></div>'
            '<div><small style="color:#9ca3af; font-weight:bold;">🚨 EN MORA</small><br><span style="font-size:24px; font-weight:bold; color:#f87171;">{} Nichos</span></div>'
            '<div><small style="color:#9ca3af; font-weight:bold;">📊 TOTAL</small><br><span style="font-size:24px; font-weight:bold;">{}</span></div>'
            '</div>', 
            qs['p'] or 0, qs['m'], qs['t']
        )
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="📊 Exportar Reporte CSV")
    def exportar_a_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Sanarate_Reporte.csv"'
        writer = csv.writer(response)
        writer.writerow(['Codigo', 'Difunto', 'Propietario', 'Monto Arbitrio', 'Lat', 'Lng'])
        for n in queryset: 
            writer.writerow([n.codigo, n.nombre_difunto, n.propietario, n.monto_arbitrio, n.lat, n.lng])
        return response

    @admin.action(description="🏴 Marcar como Exhumado")
    def marcar_exhumado_masivo(self, request, queryset):
        queryset.update(esta_exhumado=True)
