import xlwt
from django.http import HttpResponse
from django.contrib import admin
from .models import Nicho
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class NichoResource(resources.ModelResource):
    class Meta:
        model = Nicho
        fields = ('id', 'codigo', 'nombre_difunto', 'propietario', 'monto_arbitrio', 'fecha_vencimiento')

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin):
    resource_class = NichoResource
    list_display = ('codigo', 'nombre_difunto', 'propietario', 'status_financiero', 'estado_legal', 'consola_tecnologica')
    list_editable = ('nombre_difunto', 'propietario')
    search_fields = ('codigo', 'nombre_difunto', 'propietario')
    ordering = ('id',) 
    list_per_page = 50 
    list_filter = ('esta_exhumado', 'monto_arbitrio', ('fecha_vencimiento', admin.DateFieldListFilter), 'fecha_pago')
    actions = ['exportar_a_excel_veloz', 'marcar_exhumado_masivo']

    def estado_legal(self, obj):
        info = obj.semaforo_estado 
        return format_html('<span style="background:{}; color:white; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:bold; text-transform:uppercase;">{}</span>', info['color'], info['estado'])
    estado_legal.short_description = "Estado Legal"

    def status_financiero(self, obj):
        if obj.monto_arbitrio > 0:
            return format_html('<b style="color:#28a745;">✅ Q{}</b>', obj.monto_arbitrio)
        return mark_safe('<b style="color:#dc3545;">🚨 MORA</b>')
    status_financiero.short_description = "Finanzas"

    def consola_tecnologica(self, obj):
        links = []
        # --- 1. TÉCNICO E IDENTIFICACIÓN ---
        links.append(format_html('<a href="{}" target="_blank" title="FICHA PRO" style="text-decoration:none; font-size:18px;">💎</a>', reverse('ficha_tecnica_pro', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Reporte Inspección" style="text-decoration:none; margin-left:8px; font-size:18px;">🔍</a>', reverse('reporte_inspeccion', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Título de Propiedad" style="text-decoration:none; margin-left:8px; font-size:18px;">📜</a>', reverse('generar_titulo_propiedad', args=[obj.id])))
        
        # --- 2. GESTIÓN OPERATIVA ---
        links.append(format_html('<a href="{}" target="_blank" title="Acta de Inhumación" style="text-decoration:none; margin-left:8px; font-size:18px;">📖</a>', reverse('acta_inhumacion', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Permiso Construcción" style="text-decoration:none; margin-left:8px; font-size:18px;">🧱</a>', reverse('permiso_construccion', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Traspaso Derechos" style="text-decoration:none; margin-left:8px; font-size:18px;">✍️</a>', reverse('traspaso_derechos', args=[obj.id])))

        # --- 3. LEGAL Y FINANCIERO ---
        links.append(format_html('<a href="{}" target="_blank" title="Certificación Solvencia" style="text-decoration:none; margin-left:8px; font-size:18px;">🏅</a>', reverse('solvencia_municipal', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Aviso de Mora" style="text-decoration:none; margin-left:8px; font-size:18px;">✉️</a>', reverse('aviso_mora', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Orden Exhumación" style="text-decoration:none; margin-left:8px; font-size:18px;">🏴</a>', reverse('orden_exhumacion', args=[obj.id])))
        
        # --- 4. UBICACIÓN ---
        if obj.lat and obj.lng:
            url_vuelo = f"/mapa/?lat={obj.lat}&lng={obj.lng}&z=21&codigo={obj.codigo}&popup=true"
            links.append(format_html('<a href="{}" target="_blank" title="Mapa Satelital" style="text-decoration:none; margin-left:8px; font-size:18px;">📍</a>', url_vuelo))
            
        return mark_safe(f'<div style="display:flex; justify-content:center; align-items:center;">{" ".join(links)}</div>')
    consola_tecnologica.short_description = "Acciones G.I.S."

    @admin.action(description="🚀 Exportar Excel Rápido")
    def exportar_a_excel_veloz(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Sanarate_Reporte.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Nichos')
        for i, col in enumerate(['Codigo', 'Difunto', 'Propietario', 'Monto']):
            ws.write(0, i, col)
        for r, obj in enumerate(queryset, 1):
            ws.write(r, 0, obj.codigo); ws.write(r, 1, obj.nombre_difunto); ws.write(r, 2, obj.propietario); ws.write(r, 3, obj.monto_arbitrio)
        wb.save(response)
        return response

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request).aggregate(p=Sum('monto_arbitrio'), m=Count('id', filter=Q(monto_arbitrio=0)), t=Count('id'))
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

    @admin.action(description="🏴 Ejecutar Exhumación (Liberar Nicho)")
    def marcar_exhumado_masivo(self, request, queryset):
        queryset.update(
            nombre_difunto="", 
            propietario="", 
            monto_arbitrio=0.00, 
            esta_exhumado=True,
            fecha_pago=None,
            fecha_vencimiento=None
        )
        self.message_user(request, "Exhumación masiva completada. Los nichos ahora aparecen como DISPONIBLES.")

from .models import ReporteDano

@admin.register(ReporteDano)
class ReporteDanoAdmin(admin.ModelAdmin):
    list_display = ('nicho_link', 'alerta_urgencia', 'estado_visual', 'fecha_reporte', 'reportado_por', 'ver_foto')
    list_filter = ('estado', 'nivel_urgencia', 'fecha_reporte')
    search_fields = ('nicho__codigo', 'descripcion')
    list_editable = ('estado',)
    readonly_fields = ('fecha_reporte', 'reportado_por')

    def nicho_link(self, obj):
        url = reverse('admin:registros_nicho_change', args=[obj.nicho.id])
        return format_html('<a href="{}" style="font-weight:bold; color:#1e40af;">{}</a>', url, obj.nicho.codigo)
    nicho_link.short_description = "Nicho"

    def alerta_urgencia(self, obj):
        colores = {'LEVE': '#3b82f6', 'MODERADO': '#f59e0b', 'CRITICO': '#ef4444'}
        color = colores.get(obj.nivel_urgencia, '#6b7280')
        return format_html('<span style="color:{}; font-weight:bold;">● {}</span>', color, obj.get_nivel_urgencia_display())
    alerta_urgencia.short_description = "Urgencia"

    def estado_visual(self, obj):
        return format_html('<b>{}</b>', obj.get_estado_display())
    estado_visual.short_description = "Estado"

    def ver_foto(self, obj):
        if obj.foto_evidencia:
            return format_html('<a href="{}" target="_blank">🖼️ Ver Foto</a>', obj.foto_evidencia.url)
        return "Sin foto"
    ver_foto.short_description = "Evidencia"

# Re-configuración para corregir el error de list_editable
admin.site.unregister(ReporteDano)

@admin.register(ReporteDano)
class ReporteDanoAdmin(admin.ModelAdmin):
    # Agregamos 'estado' directamente para que sea editable
    list_display = ('nicho_link', 'alerta_urgencia', 'estado', 'fecha_reporte', 'reportado_por', 'ver_foto')
    list_filter = ('estado', 'nivel_urgencia', 'fecha_reporte')
    search_fields = ('nicho__codigo', 'descripcion')
    list_editable = ('estado',) 
    readonly_fields = ('fecha_reporte', 'reportado_por')

    def nicho_link(self, obj):
        url = reverse('admin:registros_nicho_change', args=[obj.nicho.id])
        return format_html('<a href="{}" style="font-weight:bold; color:#1e40af;">{}</a>', url, obj.nicho.codigo)
    nicho_link.short_description = "Nicho"

    def alerta_urgencia(self, obj):
        colores = {'LEVE': '#3b82f6', 'MODERADO': '#f59e0b', 'CRITICO': '#ef4444'}
        color = colores.get(obj.nivel_urgencia, '#6b7280')
        return format_html('<span style="color:{}; font-weight:bold;">● {}</span>', color, obj.get_nivel_urgencia_display())
    alerta_urgencia.short_description = "Urgencia"

    def ver_foto(self, obj):
        if obj.foto_evidencia:
            return format_html('<a href="{}" target="_blank">🖼️ Ver Foto</a>', obj.foto_evidencia.url)
        return "Sin foto"
    ver_foto.short_description = "Evidencia"
