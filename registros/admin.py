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
    list_per_page = 50 # Hace que el panel cargue más rápido
    
    list_filter = ('esta_exhumado', 'monto_arbitrio', ('fecha_vencimiento', admin.DateFieldListFilter), 'fecha_pago')
    
    # Nueva acción rápida
    actions = ['exportar_a_excel_veloz', 'marcar_exhumado_masivo']

    @admin.action(description="🚀 Exportar Excel Rápido")
    def exportar_a_excel_veloz(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Sanarate_Reporte.xls"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Nichos')

        # Estilo para el encabezado
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Codigo', 'Nombre Difunto', 'Propietario', 'Monto Arbitrio', 'Vencimiento']

        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        # Datos
        font_style = xlwt.XFStyle()
        rows = queryset.values_list('codigo', 'nombre_difunto', 'propietario', 'monto_arbitrio', 'fecha_vencimiento')
        
        for row_num, row in enumerate(rows, 1):
            for col_num, cell_value in enumerate(row):
                # Convertir fecha a string para evitar líos
                if hasattr(cell_value, 'isoformat'):
                    cell_value = cell_value.strftime('%d/%m/%Y')
                ws.write(row_num, col_num, cell_value, font_style)

        wb.save(response)
        return response

    def estado_legal(self, obj):
        info = obj.semaforo_estado 
        return format_html('<span style="background:{}; color:white; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:bold;">{}</span>', info['color'], info['estado'])

    def status_financiero(self, obj):
        if obj.monto_arbitrio > 0:
            return format_html('<b style="color:#28a745;">✅ Q{}</b>', obj.monto_arbitrio)
        return mark_safe('<b style="color:#dc3545;">🚨 MORA</b>')

    def consola_tecnologica(self, obj):
        links = []
        links.append(format_html('<a href="/imprimir/{}/" target="_blank" title="Ficha" style="text-decoration:none; font-size:18px;">📄</a>', obj.id))
        links.append(format_html('<a href="{}" target="_blank" title="Título" style="text-decoration:none; margin-left:10px; font-size:18px;">📜</a>', reverse('generar_titulo_propiedad', args=[obj.id])))
        if obj.lat and obj.lng:
            links.append(format_html('<a href="/mapa/?lat={}&lng={}&z=20" title="Mapa" style="text-decoration:none; margin-left:10px; font-size:18px;">📍</a>', obj.lat, obj.lng))
        return mark_safe(f'<div style="display:flex; justify-content:center;">{" ".join(links)}</div>')

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request).aggregate(p=Sum('monto_arbitrio'), m=Count('id', filter=Q(monto_arbitrio=0)), t=Count('id'))
        extra_context = extra_context or {}
        extra_context['title'] = format_html('<div style="background:#111827; padding:20px; border-radius:12px; color:white; display:flex; gap:50px; margin-bottom:20px;"><div><small style="color:#9ca3af;">💰 RECAUDACIÓN</small><br><span style="color:#4ade80; font-size:24px; font-weight:bold;">Q{}</span></div><div><small style="color:#9ca3af;">🚨 MORA</small><br><span style="color:#f87171; font-size:24px; font-weight:bold;">{}</span></div><div><small style="color:#9ca3af;">📊 TOTAL</small><br><span style="font-size:24px; font-weight:bold;">{}</span></div></div>', qs['p'] or 0, qs['m'], qs['t'])
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="🏴 Marcar como Exhumado")
    def marcar_exhumado_masivo(self, request, queryset):
        queryset.update(esta_exhumado=True)
