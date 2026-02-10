from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa_nichos, name='index'),
    path('buscar/', views.buscar_nicho_json, name='buscar_nicho'),
    path('actualizar/', views.actualizar_posicion, name='actualizar_posicion'),
    path('titulo-pdf/<int:nicho_id>/', views.generar_titulo_pdf, name='generar_titulo_pdf'),
    # NUEVA RUTA PARA TRABAJADORES
    path('campo/', views.registro_campo_offline, name='registro_campo'),
]
