from django.urls import path
from . import views

urlpatterns = [
    # --- DASHBOARD Y MAPA ---
    path('', views.dashboard, name='dashboard'),
    path('mapa/', views.mapa_cimenterio, name='mapa_cimenterio'),
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    
    # --- DOCUMENTOS DE ALTA SEGURIDAD ---
    # Título de Propiedad
    path('nicho/<int:nicho_id>/titulo/', views.generar_titulo_propiedad, name='generar_titulo_propiedad'),
    
    # Solvencia Municipal
    path('nicho/<int:nicho_id>/solvencia/', views.pdf_solvencia_municipal, name='pdf_solvencia_municipal'),
    path('nicho/<int:nicho_id>/solvencia-pdf/', views.pdf_solvencia_municipal, name='pdf_solvencia_municipal_alt'),
    
    # Notificación de Mora
    path('nicho/<int:nicho_id>/aviso-mora/', views.pdf_notificacion_mora, name='aviso_mora'),
    path('nicho/<int:nicho_id>/aviso-mora-pdf/', views.pdf_notificacion_mora, name='pdf_notificacion_mora_alt'),
    
    # --- CONSULTA PÚBLICA (EL QR) ---
    path('consulta/<str:codigo>/', views.consulta_publica, name='consulta_publica'),
    path('consultar/<str:codigo>/', views.consulta_publica),
    
    # --- INSPECCIÓN Y REPORTES ---
    path('nicho/<int:nicho_id>/inspeccion/', views.reportar_dano, name='reporte_inspeccion'),
]
