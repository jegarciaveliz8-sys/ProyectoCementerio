from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter
from .models import Nicho, FotoCampo, Exhumacion
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Nicho)
class NichoAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    # Solo campos de texto y fecha, NADA de format_html aquí
    list_display = ('codigo', 'nombre_difunto', 'propietario', 'fecha_vencimiento')
    list_filter = ('estado_id', ('fecha_vencimiento', DateRangeFilter))
    search_fields = ('codigo', 'propietario', 'nombre_difunto')
    list_display_links = ('codigo',)

    # Esto asegura que el QR y las coordenadas se vean pero no se editen dentro del nicho
    def get_readonly_fields(self, request, obj=None):
        if obj: # Si el nicho ya existe
            return ('qr_code', 'codigo')
        return ('qr_code',)

admin.site.register(FotoCampo)
admin.site.register(Exhumacion)
