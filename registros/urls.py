from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mapa/', views.mapa_cimenterio, name='mapa_cimenterio'),
    path('api/datos/', views.datos_nichos_json, name='datos_nichos_json'),
    path('imprimir/<int:nicho_id>/', views.imprimir_ficha, name='imprimir_ficha'),
    path('imprimir-qrs/', views.imprimir_todos_qrs, name='imprimir_qrs'),
    
    # DOCUMENTOS DE PROPIEDAD Y TÉCNICOS
    path('nicho/<int:nicho_id>/titulo/', views.generar_titulo_propiedad, name='generar_titulo_propiedad'),
    path('nicho/<int:nicho_id>/ficha-pro/', views.ficha_tecnica_pro, name='ficha_tecnica_pro'),
    path('nicho/<int:nicho_id>/inspeccion/', views.pdf_reporte_inspeccion, name='reporte_inspeccion'),
    
    # TRÁMITES ADMINISTRATIVOS
    path('nicho/<int:nicho_id>/traspaso/', views.pdf_traspaso_derechos, name='traspaso_derechos'),
    path('nicho/<int:nicho_id>/construccion/', views.pdf_permiso_construccion, name='permiso_construccion'),
    path('nicho/<int:nicho_id>/acta-inhumacion/', views.pdf_acta_inhumacion, name='acta_inhumacion'),
    
    # CONTROL DE MORA Y CIERRE
    path('nicho/<int:nicho_id>/solvencia/', views.pdf_solvencia_municipal, name='solvencia_municipal'),
    path('nicho/<int:nicho_id>/aviso-mora/', views.pdf_notificacion_mora, name='aviso_mora'),
    path('nicho/<int:nicho_id>/exhumacion/', views.pdf_orden_exhumacion, name='orden_exhumacion'),
    
    path('consultar/<str:codigo>/', views.consulta_publica, name='consulta_publica'),
]
