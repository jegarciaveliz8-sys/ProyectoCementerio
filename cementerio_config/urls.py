from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from registros.views import dashboard_stats

urlpatterns = [
    path('', dashboard_stats, name='dashboard'),
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    # Todas las rutas de la app se manejan desde registros/urls.py
    path('', include('registros.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
