import csv
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Nicho, FotoCampo

@admin.register(Nicho)
class NichoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'propietario', 'nombre_difunto')
    search_fields = ('codigo', 'propietario', 'nombre_difunto', 'dpi_propietario')
    actions = ['descargar_pdf', 'exportar_excel']

    def descargar_pdf(self, request, queryset):
        from django.shortcuts import redirect
        if queryset.count() == 1:
            return redirect('generar_titulo_pdf', nicho_id=queryset[0].id)
        self.message_user(request, "Seleccione solo un registro.")
    descargar_pdf.short_description = "📄 Generar Título (PDF)"

    def exportar_excel(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_sanarate.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['Código', 'Dueño Legal', 'Difunto'])
        for n in queryset:
            writer.writerow([getattr(n,'codigo',''), getattr(n,'propietario',''), getattr(n,'nombre_difunto','')])
        return response
    exportar_excel.short_description = "📊 Exportar a Excel"

@admin.register(FotoCampo)
class FotoCampoAdmin(admin.ModelAdmin):
    # 'ver_foto' mostrará el enlace directo
    list_display = ('nicho', 'comentario', 'ver_foto')
    
    def ver_foto(self, obj):
        if obj.imagen:
            return format_html('<a href="{}" target="_blank" style="font-weight:bold; color:#2196F3;">👁️ Ver Imagen</a>', obj.imagen.url)
        return "Sin foto"
    ver_foto.short_description = "Enlace de Imagen"
