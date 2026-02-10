from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.admin_urls if hasattr(admin.site, 'admin_urls') else admin.site.urls),
    path('registros/', include('registros.urls')),
    path('', include('registros.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
