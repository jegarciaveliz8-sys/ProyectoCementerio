from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter
from .models import Nicho, FotoCampo, Exhumacion
from simple_history.admin import SimpleHistoryAdmin
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import os

# Librerías de ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- FILTRO GPS MEJORADO (Detecta 0.0 como vacío) ---
class CoordenadasFilter(admin.SimpleListFilter):
    title = 'Ubicación GPS'
    parameter_name = 'has_coords'
    def lookups(self, request, model_admin):
        return (('si', 'Con Coordenadas'), ('no', 'Sin Coordenadas'))
    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.exclude(lat__isnull=True).exclude(lat=0).exclude(lng=0)
        if self.value() == 'no':
            return queryset.filter(lat__isnull=True) | queryset.filter(lat=0) | queryset.filter(lng=0)
        return queryset

def agregar_membrete(elements):
    styles = getSampleStyleSheet()
    logo_path = "/home/jose/ProyectoCementerio/static/img/logo_muni.png"
    estilo_m = ParagraphStyle('Membrete', parent=styles['Normal'], fontSize=13, alignment=TA_CENTER, fontName='Helvetica-Bold')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=55, height=55))
    elements.append(Paragraph("MUNICIPALIDAD DE SANARATE, EL PROGRESO", estilo_m))
    elements.append(Paragraph("ADMINISTRACIÓN DE CEMENTERIOS MUNICIPALES", styles['Normal']))
    elements.append(Spacer(1, 15))

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('codigo', 'gps_status', 'boton_mapa', 'nombre_difunto', 'propietario', 'fecha_vencimiento', 'monto_arbitrio')
    list_filter = ('estado_id', ('fecha_vencimiento', DateRangeFilter), 'monto_arbitrio', CoordenadasFilter)
    search_fields = ('codigo', 'propietario', 'nombre_difunto', 'dpi_propietario')
    list_display_links = ('codigo', 'nombre_difunto')
    list_per_page = 50

    # LAS 15 ACCIONES INTACTAS
    actions = [
        'generar_pdf_reporte', 'generar_aviso_cobro', 'generar_solicitud_traspaso',
        'generar_orden_inhumacion', 'generar_orden_exhumacion', 'generar_solvencia_municipal',
        'generar_permiso_construccion', 'generar_acta_exhumacion_final_nicho',
        'renovar_6_años', 'marcar_exhumacion', 'preparar_traspaso',
        'poner_arbitrio_50', 'poner_arbitrio_150', 'limpiar_nicho_masivo'
    ]

    def gps_status(self, obj):
        # Si la latitud existe y no es 0, mostramos el icono
        if obj.lat and obj.lat != 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', "📍 SI")
        return format_html('<span style="color: #ccc;">{}</span>', "--")
    gps_status.short_description = 'GPS'

    def boton_mapa(self, obj):
        if obj.lat and obj.lat != 0:
            url = f"https://www.google.com/maps?q={obj.lat},{obj.lng}"
            return format_html('<a class="button" href="{}" target="_blank" style="background-color: #d33; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px;">{}</a>', url, "MAPA")
        return format_html('<span>{}</span>', "--")
    boton_mapa.short_description = 'Ubicación'

    @admin.action(description='📄 PDF: Reporte General')
    def generar_pdf_reporte(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        agregar_membrete(elements)
        data = [['Código', 'Difunto', 'Vencimiento', 'Monto']]
        for obj in queryset:
            f = obj.fecha_vencimiento if obj.fecha_vencimiento else "No reg."
            data.append([obj.codigo, str(obj.nombre_difunto)[:20], str(f), f"Q{obj.monto_arbitrio}"])
        t = Table(data); t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(t); doc.build(elements); return response

    @admin.action(description='💰 PDF: Aviso de COBRO')
    def generar_aviso_cobro(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph(f"AVISO DE COBRO: {obj.codigo}", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='📜 PDF: Solvencia Municipal')
    def generar_solvencia_municipal(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("SOLVENCIA MUNICIPAL", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='🏗️ PDF: Permiso de Construcción')
    def generar_permiso_construccion(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("PERMISO DE CONSTRUCCIÓN", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='📑 PDF: Acta de Exhumación (Nicho)')
    def generar_acta_exhumacion_final_nicho(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("ACTA DE EXHUMACIÓN", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='📝 PDF: Formulario de TRASPASO')
    def generar_solicitud_traspaso(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("TRASPASO", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='⚰️ PDF: Orden de INHUMACIÓN')
    def generar_orden_inhumacion(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("INHUMACIÓN", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='💀 PDF: Orden de EXHUMACIÓN')
    def generar_orden_exhumacion(self, request, queryset):
        response = HttpResponse(content_type='application/pdf'); doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        for obj in queryset: agregar_membrete(elements); elements.append(Paragraph("ORDEN EXHUMACIÓN", getSampleStyleSheet()['Heading2']))
        doc.build(elements); return response

    @admin.action(description='🔄 LIMPIAR: Volver a Disponible')
    def limpiar_nicho_masivo(self, request, queryset):
        queryset.update(estado_id=1, nombre_difunto='', propietario='', dpi_propietario='', monto_arbitrio=0.00)

    @admin.action(description='📅 FECHA: Renovar 6 años')
    def renovar_6_años(self, request, queryset):
        queryset.update(fecha_vencimiento=timezone.now().date() + timedelta(days=365*6), estado_id=2)

    @admin.action(description='💀 ESTADO: Marcar EXHUMACIÓN')
    def marcar_exhumacion(self, request, queryset):
        queryset.update(estado_id=3)

    @admin.action(description='📝 TRASPASO: Iniciar trámite')
    def preparar_traspaso(self, request, queryset):
        queryset.update(propietario='EN TRÁMITE DE TRASPASO')

    @admin.action(description='💰 COBRO: Q50.00')
    def poner_arbitrio_50(self, request, queryset):
        queryset.update(monto_arbitrio=50.00)

    @admin.action(description='💰 COBRO: Q150.00')
    def poner_arbitrio_150(self, request, queryset):
        queryset.update(monto_arbitrio=150.00)

@admin.register(Exhumacion)
class ExhumacionAdmin(admin.ModelAdmin):
    list_display = ('nicho', 'fecha_exhumacion')
    search_fields = ('nicho__codigo',)
    autocomplete_fields = ['nicho']
    actions = ['generar_etiqueta_restos']

    @admin.action(description="🏷️ PDF: Etiqueta de Identificación")
    def generar_etiqueta_restos(self, request, queryset):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=etiqueta.pdf"
        doc = SimpleDocTemplate(response, pagesize=letter); elements = []
        styles = getSampleStyleSheet()
        for obj in queryset:
            data = [[Paragraph(f"<b>NICHO:</b> {obj.nicho.codigo}", styles['Normal'])],
                    [Paragraph(f"<b>DIFUNTO:</b> {obj.nicho.nombre_difunto}", styles['Normal'])]]
            t = Table(data, colWidths=[300])
            t.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 2, colors.black)]))
            elements.append(t); elements.append(Spacer(1, 20))
        doc.build(elements); return response

@admin.register(FotoCampo)
class FotoCampoAdmin(admin.ModelAdmin):
    list_display = ('nicho',)
    search_fields = ('nicho__codigo',)
    autocomplete_fields = ['nicho']
