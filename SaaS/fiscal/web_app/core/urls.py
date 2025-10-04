from django.urls import path
from . import views
from . import views_certificado

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # NFe
    path('nfe/', views.nfe_list, name='nfe_list'),
    path('nfe/<int:pk>/', views.nfe_detail, name='nfe_detail'),
    
    # CTe
    path('cte/', views.cte_list, name='cte_list'),
    path('cte/<int:pk>/', views.cte_detail, name='cte_detail'),
    
    # Logs e Analytics
    path('logs/', views.import_logs, name='import_logs'),
    path('analytics/', views.analytics, name='analytics'),
    
    # Certificados e Consultas SEFAZ
    path('certificados/', views_certificado.certificados_list, name='certificados_list'),
    path('certificados/upload/', views_certificado.certificado_upload, name='certificado_upload'),
    path('certificados/<int:certificado_id>/consultar/', views_certificado.consulta_sefaz, name='consulta_sefaz'),
    path('consultas/<int:consulta_id>/resultado/', views_certificado.consulta_resultado, name='consulta_resultado'),
    path('consultas/dashboard/', views_certificado.dashboard_consultas, name='dashboard_consultas'),
    path('configuracoes/consulta/', views_certificado.configuracoes_consulta, name='configuracoes_consulta'),
    
    # API Documentos
    path('api/documento/<int:documento_id>/importar/', views_certificado.importar_documento, name='importar_documento'),
]
