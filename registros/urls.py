from django.urls import path
from . import views

urlpatterns = [
    # 📊 PORTADA: El Dashboard con gráficas (Nivel Mundial)
    path('', views.dashboard, name='dashboard'),
    
    # 🛰️ MAPA: El sistema G.I.S. interactivo
    path('mapa/', views.mapa_cimenterio, name='mapa_nichos'),
    
    # 🔌 SERVICIOS: API e Impresión
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    path('imprimir/<int:nicho_id>/', views.imprimir_ficha, name='imprimir_ficha'),
]
