from django.urls import path
from . import views

urlpatterns = [
    # 📊 PORTADA: El Dashboard con gráficas
    path('', views.dashboard, name='dashboard'),
    
    # 🛰️ MAPA: El sistema G.I.S. interactivo
    path('mapa/', views.mapa_cimenterio, name='mapa_cimenterio'),
    
    # 🔌 SERVICIOS: API e Impresión
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    path('imprimir/<int:nicho_id>/', views.imprimir_ficha, name='imprimir_ficha'),
    
    # 🖨️ IMPRESIÓN MASIVA
    path('imprimir-qrs/', views.imprimir_todos_qrs, name='imprimir_qrs'),

    # 📜 TÍTULO DE PROPIEDAD PROFESIONAL (Esta es la que faltaba)
    path('nicho/<int:nicho_id>/titulo/', views.generar_titulo_propiedad, name='generar_titulo_propiedad'),
    path('consultar/<str:codigo>/', views.consulta_publica, name='consulta_publica'),
]
