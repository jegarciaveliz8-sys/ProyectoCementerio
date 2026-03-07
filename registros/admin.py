import urllib.parse
import xlwt
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.utils.safestring import mark_safe
from .models import Nicho, ReporteDano
from import_export.admin import ImportExportModelAdmin
from django.contrib.contenttypes.models import ContentType

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin):
    list_per_page = 50
    ordering = ('codigo',)
    
    # 1. Agregamos 'estado_pago' para ver el semáforo
    list_display = (
        'codigo', 'estado_pago', 'nombre_difunto_corto', 'lat', 'lng', 
        'monto_arbitrio', 'ver_documento', 'ver_en_mapa', 
        'boton_gps', 'accion_cobro'
    )
    
    list_editable = ('lat', 'lng', 'monto_arbitrio')
    
    # 2. Filtros potentes a la derecha
    list_filter = ('esta_exhumado', ('fecha_vencimiento', admin.DateFieldListFilter))
    
    # 3. Buscador ampliado
    search_fields = ('codigo', 'nombre_difunto', 'propietario')
    
    fields = ('codigo', 'propietario', 'nombre_difunto', 'monto_arbitrio', 'fecha_vencimiento', 'lat', 'lng', 'foto_nicho', 'titulo_propiedad', 'acta_exhumacion', 'notas_legales')
    readonly_fields = ('ver_foto_grande', 'ver_qr_grande')
    actions = ['exportar_excel_gerencial']

    # --- SEMÁFORO VISUAL ---
    def estado_pago(self, obj):
        data = obj.semaforo_estado
        return format_html(
            '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{};margin-right:5px;" title="{}"></span>',
            data['color'], data['estado']
        )
    estado_pago.short_description = "ST"

    def nombre_difunto_corto(self, obj):
        nombre = obj.nombre_difunto or "DISPONIBLE"
        return nombre[:25] + "..." if len(nombre) > 25 else nombre
    nombre_difunto_corto.short_description = "DIFUNTO"

    def ver_en_mapa(self, obj):
        if obj.lat and obj.lng:
            url = f"https://www.google.com/maps?q={obj.lat},{obj.lng}"
            return format_html('<a href="{}" target="_blank" style="background:#ea4335;color:white;padding:2px 5px;border-radius:3px;text-decoration:none;font-size:9px;">📍 VER</a>', url)
        return "-"
    ver_en_mapa.short_description = "MAPA"

    def ver_documento(self, obj):
        if obj.titulo_propiedad:
            return format_html('<a href="{}" target="_blank" style="background:#2563eb;color:white;padding:2px 5px;border-radius:3px;text-decoration:none;font-size:9px;">📄 TIT</a>', obj.titulo_propiedad.url)
        return mark_safe('<span style="color:#cbd5e1;font-size:9px;">-</span>')
    ver_documento.short_description = "DOC"

    def boton_gps(self, obj):
        js = f"navigator.geolocation.getCurrentPosition(function(p){{ var r=document.activeElement.closest('tr'); var lt=r.querySelector('.field-lat input'); var ln=r.querySelector('.field-lng input'); lt.value=p.coords.latitude.toFixed(8); ln.value=p.coords.longitude.toFixed(8); lt.style.background='#bbf7d0'; ln.style.background='#bbf7d0'; }});"
        return mark_safe(f'<button type="button" onclick="{js}" style="background:#0f172a;color:white;border:none;padding:4px 6px;border-radius:3px;font-size:9px;cursor:pointer;">🛰️ GPS</button>')
    boton_gps.short_description = "CAPTURAR"

    def accion_cobro(self, obj):
        if obj.monto_arbitrio > 0:
            msg = urllib.parse.quote(f"Muni Sanarate: Deuda Q{obj.monto_arbitrio} nicho {obj.codigo}.")
            return format_html('<a href="https://wa.me/?text={}" target="_blank" style="color:#16a34a;font-weight:bold;font-size:11px;">📲 WA</a>', msg)
        return "-"

    def ver_logs(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        url = f"/admin/auditlog/logentry/?object_id={obj.pk}&content_type={ct.pk}"
        return format_html('<a href="{}" style="font-size:10px;color:#64748b;">🕒 Hist</a>', url)
    ver_logs.short_description = "AUDIT"

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        stats = qs.aggregate(mora=Sum('monto_arbitrio'), total=Count('id'), mapeados=Count('id', filter=Q(lat__gt=0)))
        extra_context = extra_context or {}
        custom_style = """
        <style>
            #content { max-width: 98% !important; }
            .results table { width: 100% !important; }
            .column-lat input, .column-lng input { width: 90px !important; border: 1px solid #475569 !important; padding: 4px !important; background: white !important; color: black !important; }
            .column-monto_arbitrio input { width: 70px !important; border: 1px solid #475569 !important; background: #fefce8 !important; font-weight: bold; color: #b91c1c; }
            .column-codigo { font-weight: bold; }
        </style>
        """
        header = f"""
        {custom_style}
        <div style="background:#0f172a;color:white;padding:15px;border-radius:8px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
            <div><small>MORA TOTAL</small><br><b style="font-size:20px;color:#f87171;">Q{stats['mora'] or 0:,.2f}</b></div>
            <div style="text-align:right;"><small>CONTROL CATASTRO</small><br><b style="font-size:18px;">{stats['mapeados']} / {stats['total']}</b> Georreferenciados</div>
        </div>
        """
        extra_context['title'] = mark_safe(header)
        return super().changelist_view(request, extra_context=extra_context)

    def exportar_excel_gerencial(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Catastro_Cementerio.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Datos')
        for i, col in enumerate(['CODIGO', 'DIFUNTO', 'PROPIETARIO', 'MORA', 'LAT', 'LNG']): ws.write(0, i, col)
        for r, obj in enumerate(queryset, 1):
            ws.write(r, 0, obj.codigo); ws.write(r, 1, obj.nombre_difunto); ws.write(r, 2, obj.propietario); ws.write(r, 3, float(obj.monto_arbitrio)); ws.write(r, 4, obj.lat); ws.write(r, 5, obj.lng)
        wb.save(response)
        return response
    exportar_excel_gerencial.short_description = "📊 Exportar Catastro a Excel"

    def ver_foto_grande(self, obj):
        if obj.foto_nicho: return format_html('<img src="{}" style="max-width:400px;" />', obj.foto_nicho.url)
        return "Sin foto"
    def ver_qr_grande(self, obj):
        if obj.qr_code: return format_html('<img src="{}" style="width:200px;" />', obj.qr_code.url)
        return "Sin QR"

admin.site.register(ReporteDano)
