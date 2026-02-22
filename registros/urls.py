from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa_nichos, name='mapa_nichos_root'),
    path('mapa/', views.mapa_nichos, name='mapa_nichos'),
    path('actualizar-posicion/', views.actualizar_posicion, name='actualizar_posicion'),
    path('buscar_nicho_json/', views.buscar_nicho_json, name='buscar_nicho_json'),
    path('generar-titulo/<int:nicho_id>/', views.generar_titulo_pdf, name='generar_titulo_pdf'),
    
    # Nueva ruta para la Ficha Digital escaneada por QR
    path('nicho/<str:codigo>/', views.detalle_nicho_publico, name='detalle_nicho_publico'),
]
