from django.urls import path
from . import views

urlpatterns = [
    # 📊 PORTADA: El Dashboard con gráficas
    path('', views.dashboard, name='dashboard'),
    
    # 🛰️ MAPA: El sistema G.I.S. interactivo con Radar y Buscador
    path('mapa/', views.mapa_cimenterio, name='mapa_nichos'),
    
    # 🔌 SERVICIOS: API e Impresión
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    path('imprimir/<int:nicho_id>/', views.imprimir_ficha, name='imprimir_ficha'),
    
    # 🖨️ IMPRESIÓN MASIVA: Generador de etiquetas QR para el cementerio
    path('imprimir-qrs/', views.imprimir_todos_qrs, name='imprimir_qrs'),
]
