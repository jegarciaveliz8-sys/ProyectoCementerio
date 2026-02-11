from django.urls import path
from . import views

urlpatterns = [
    # El Mapa como página principal (raíz)
    path('', views.mapa_nichos, name='mapa_nichos_root'),
    
    # NUEVA: Esta es la que resuelve el error 404 del Admin
    path('mapa/', views.mapa_nichos, name='mapa_nichos'),
    
    # Ruta para buscar nichos (la usa el buscador del mapa)
    path('buscar_nicho_json/', views.buscar_nicho_json, name='buscar_nicho_json'),
    
    # Documentos Legales
    path('generar-titulo/<int:nicho_id>/', views.generar_titulo_pdf, name='generar_titulo_pdf'),
    path('exhumacion/pdf/<int:exhumacion_id>/', views.generar_acta_exhumacion_pdf, name='generar_acta_exhumacion_pdf'),
    
    # Registro de campo
    path('registro-campo/', views.registro_campo_offline, name='registro_campo_offline'),
]
