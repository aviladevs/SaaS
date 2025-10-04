"""
Permissions e decorators para RBAC
"""
from rest_framework.permissions import BasePermission
from functools import wraps
from django.http import HttpResponseForbidden


class IsTenantMember(BasePermission):
    """
    Permissão que verifica se o usuário pertence ao tenant da requisição
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Verificar se usuário pertence ao tenant
        if hasattr(request, 'tenant') and request.tenant:
            return request.user.tenant == request.tenant
        
        return False


class HasTenantPermission(BasePermission):
    """
    Permissão que verifica se o usuário tem uma permissão específica no tenant
    """
    required_resource = None
    required_action = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Obter resource e action da view ou da classe de permissão
        resource = getattr(view, 'required_resource', self.required_resource)
        action = getattr(view, 'required_action', self.required_action)
        
        if not resource or not action:
            # Se não especificado, verificar apenas se é membro do tenant
            return IsTenantMember().has_permission(request, view)
        
        # Verificar se usuário tem a permissão específica
        return request.user.has_permission(resource, action)


class IsTenantOwner(BasePermission):
    """
    Permissão que verifica se o usuário é o owner do tenant
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if hasattr(request, 'tenant') and request.tenant:
            return request.user.email == request.tenant.owner_email
        
        return False


def require_tenant(view_func):
    """
    Decorator que marca uma view como requerendo tenant
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant') or not request.tenant:
            return HttpResponseForbidden("Tenant não identificado.")
        return view_func(request, *args, **kwargs)
    
    wrapper.requires_tenant = True
    return wrapper


def require_permission(resource, action):
    """
    Decorator que verifica se usuário tem permissão específica
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Autenticação necessária.")
            
            if not request.user.is_superuser and not request.user.has_permission(resource, action):
                return HttpResponseForbidden(
                    f"Você não tem permissão para {action} {resource}."
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_tenant_owner(view_func):
    """
    Decorator que verifica se usuário é owner do tenant
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Autenticação necessária.")
        
        if not request.user.is_superuser:
            if not hasattr(request, 'tenant') or not request.tenant:
                return HttpResponseForbidden("Tenant não identificado.")
            
            if request.user.email != request.tenant.owner_email:
                return HttpResponseForbidden("Apenas o owner do tenant pode acessar este recurso.")
        
        return view_func(request, *args, **kwargs)
    return wrapper
