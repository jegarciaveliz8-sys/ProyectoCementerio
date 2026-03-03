from django.urls import path
from . import views

urlpatterns = [
    # El mapa principal
    path('', views.mapa_cimenterio, name='mapa_nichos_root'),
    path('mapa/', views.mapa_cimenterio, name='mapa_nichos'),
    
    # La API para que el mapa lea los 10,000 puntos rápido
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    path('imprimir/<int:nicho_id>/', views.imprimir_ficha, name='imprimir_ficha'),
]
