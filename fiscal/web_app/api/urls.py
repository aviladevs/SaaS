"""
URLs da API REST para App Mobile
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from . import views_webhooks

# Router para viewsets
router = DefaultRouter()
router.register('nfe', views.NFeViewSet, basename='nfe')
router.register('cte', views.CTeViewSet, basename='cte')
router.register('logs', views.ImportLogViewSet, basename='logs')
router.register('webhooks', views_webhooks.WebhookViewSet, basename='webhooks')

urlpatterns = [
    # Auth token para app mobile
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    
    # Endpoints customizados
    path('dashboard/', views.dashboard_api, name='api_dashboard'),
    path('statistics/', views.statistics_api, name='api_statistics'),
    path('search/', views.search_api, name='api_search'),
    
    # Endpoints de integração
    path('integracoes/testar/', views_webhooks.testar_integracao, name='api_testar_integracao'),
    path('integracoes/disparar/', views_webhooks.disparar_evento, name='api_disparar_evento'),
    path('integracoes/eventos/', views_webhooks.eventos_disponiveis, name='api_eventos'),
    
    # Router URLs
    path('', include(router.urls)),
]
