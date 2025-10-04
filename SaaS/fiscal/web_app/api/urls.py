"""
URLs da API REST para App Mobile
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Router para viewsets
router = DefaultRouter()
router.register('nfe', views.NFeViewSet, basename='nfe')
router.register('cte', views.CTeViewSet, basename='cte')
router.register('logs', views.ImportLogViewSet, basename='logs')

urlpatterns = [
    # Auth token para app mobile
    path('auth/login/', obtain_auth_token, name='api_token_auth'),
    
    # Endpoints customizados
    path('dashboard/', views.dashboard_api, name='api_dashboard'),
    path('statistics/', views.statistics_api, name='api_statistics'),
    path('search/', views.search_api, name='api_search'),
    
    # Router URLs
    path('', include(router.urls)),
]
