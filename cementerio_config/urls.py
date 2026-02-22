from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from registros.views import dashboard_stats, buscador_nichos

urlpatterns = [
    # Dashboard de estadísticas
    path('admin/dashboard/', dashboard_stats, name='admin_dashboard'),
    
    # Buscador para celular (lo que buscabas)
    path('buscar/', buscador_nichos, name='buscador'),
    
    path('admin/', admin.site.urls),
    path('registros/', include('registros.urls')),
    path('', include('registros.urls')),
]

# Esto permite que las fotos y los QR se vean en el navegador
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
