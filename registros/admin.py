import xlwt
from django.http import HttpResponse
from django.contrib import admin
from .models import Nicho, ReporteDano
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# 1. Configuración para que las fotos aparezcan DENTRO del nicho
class ReporteDanoInline(admin.TabularInline):
    model = ReporteDano
    extra = 1
    fields = ('foto_evidencia', 'descripcion', 'estado', 'nivel_urgencia')
    verbose_name = "Fotografía / Reporte de Campo"
    verbose_name_plural = "Historial de Fotografías y Daños"

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
    
    # ESTA LÍNEA UNE LOS DOS MODELOS:
    inlines = [ReporteDanoInline]

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
        links.append(format_html('<a href="{}" target="_blank" title="FICHA PRO" style="text-decoration:none; font-size:18px;">💎</a>', reverse('ficha_tecnica_pro', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Reporte Inspección" style="text-decoration:none; margin-left:8px; font-size:18px;">🔍</a>', reverse('reporte_inspeccion', args=[obj.id])))
        links.append(format_html('<a href="{}" target="_blank" title="Título de Propiedad" style="text-decoration:none; margin-left:8px; font-size:18px;">📜</a>', reverse('generar_titulo_propiedad', args=[obj.id])))
        
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

    @admin.action(description="🏴 Ejecutar Exhumación (Liberar Nicho)")
    def marcar_exhumado_masivo(self, request, queryset):
        queryset.update(nombre_difunto="", propietario="", monto_arbitrio=0.00, esta_exhumado=True)
        self.message_user(request, "Exhumación masiva completada.")

@admin.register(ReporteDano)
class ReporteDanoAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'estado', 'nivel_urgencia', 'fecha_reporte', 'ver_foto')
    list_editable = ('estado',)
    
    def ver_foto(self, obj):
        if obj.foto_evidencia:
            return format_html('<a href="{}" target="_blank">🖼️ Ver</a>', obj.foto_evidencia.url)
        return "Sin foto"
