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
    list_filter = ('esta_exhumado', 'monto_arbitrio', ('fecha_vencimiento', admin.DateFieldListFilter))
    actions = ['exportar_a_excel']

    def status_financiero(self, obj):
        if obj.monto_arbitrio > 0:
            return format_html('<b style="color:#28a745;">✅ Q{}</b>', obj.monto_arbitrio)
        return mark_safe('<b style="color:#dc3545;">🚨 MORA</b>')

    def indicador_tiempo(self, obj):
        if not obj.fecha_vencimiento: 
            return mark_safe('<span style="color:#f39c12;">SIN FECHA</span>')
        dias = (obj.fecha_vencimiento - timezone.now().date()).days
        color = "#28a745" if dias > 0 else "#dc3545"
        return format_html('<b style="color:{};">{}d</b>', color, dias)

    def consola_tecnologica(self, obj):
        links = []
        if obj.qr_code:
            # Aquí estaba el error, ahora está corregido pasando la URL del QR
            links.append(format_html(
                '<img src="{}" style="width:30px; border-radius:4px; cursor:zoom-in; transition: 0.3s;" '
                'onmouseover="this.style.transform=\'scale(8)\'; this.style.zIndex=\'1000\'; this.style.position=\'absolute\';" '
                'onmouseout="this.style.transform=\'scale(1)\'; this.style.position=\'static\';"/>', 
                obj.qr_code.url
            ))
        if obj.lat:
            links.append(mark_safe('<a href="/mapa/" style="font-size:20px; text-decoration:none; margin-left:10px;">📍</a>'))
        
        return mark_safe(f'<div style="display:flex; align-items:center;">{" ".join(links)}</div>')

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request).aggregate(
            p=Sum('monto_arbitrio'), 
            m=Count('id', filter=Q(monto_arbitrio=0)), 
            t=Count('id')
        )
        extra_context = extra_context or {}
        # Dashboard limpio y sin errores de agregación
        extra_context['title'] = format_html(
            '<div style="background:#111827; padding:20px; border-radius:12px; color:white; display:flex; gap:50px; border-bottom:5px solid #374151;">'
            '<div><small style="color:#9ca3af; font-weight:bold;">💰 RECAUDACIÓN</small><br><span style="font-size:24px; font-weight:bold; color:#4ade80;">Q{}</span></div>'
            '<div><small style="color:#9ca3af; font-weight:bold;">🚨 MOROSIDAD</small><br><span style="font-size:24px; font-weight:bold; color:#f87171;">{} Nichos</span></div>'
            '<div><small style="color:#9ca3af; font-weight:bold;">📊 REGISTROS</small><br><span style="font-size:24px; font-weight:bold;">{}</span></div>'
            '</div>', 
            qs['p'] or 0, qs['m'], qs['t']
        )
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="📊 Exportar Reporte")
    def exportar_a_excel(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Sanarate_Reporte.csv"'
        writer = csv.writer(response)
        writer.writerow(['Codigo', 'Difunto', 'Arbitrio'])
        for n in queryset: 
            writer.writerow([n.codigo, n.nombre_difunto, n.monto_arbitrio])
        return response
