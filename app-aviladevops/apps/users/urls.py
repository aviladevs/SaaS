"""
URLs para o sistema de autenticação multi-tenant
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users import views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet, basename='tenant')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'oauth-providers', views.OAuthProviderViewSet, basename='oauth-provider')
router.register(r'invitations', views.UserInvitationViewSet, basename='invitation')
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')
router.register(r'mfa', views.MFAViewSet, basename='mfa')

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
]
