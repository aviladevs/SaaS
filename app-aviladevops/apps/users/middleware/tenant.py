"""
Middleware para detecção e isolamento de tenant baseado em subdomínio
"""
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from apps.users.models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware para identificar e anexar tenant ao request baseado no domínio/subdomínio
    """
    
    def process_request(self, request):
        # Ignorar para rotas de admin e static
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        # Obter hostname da requisição
        hostname = request.get_host().split(':')[0]
        
        # Tentar encontrar tenant pelo domínio completo
        try:
            tenant = Tenant.objects.get(domain=hostname)
        except Tenant.DoesNotExist:
            # Tentar extrair subdomínio se for um domínio composto
            parts = hostname.split('.')
            if len(parts) > 2:
                # Exemplo: cliente.aviladevops.com.br -> cliente
                subdomain = parts[0]
                try:
                    tenant = Tenant.objects.get(slug=subdomain)
                except Tenant.DoesNotExist:
                    tenant = None
            else:
                tenant = None
        
        # Verificar se tenant está ativo
        if tenant:
            if tenant.status == 'suspended':
                return HttpResponseForbidden("Tenant suspenso. Entre em contato com o suporte.")
            elif tenant.status == 'inactive':
                return HttpResponseForbidden("Tenant inativo.")
        
        # Anexar tenant ao request
        request.tenant = tenant
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Verificar se a view requer tenant e se está disponível
        """
        # Verificar se a view requer tenant
        requires_tenant = getattr(view_func, 'requires_tenant', False)
        
        if requires_tenant and not request.tenant:
            return HttpResponseForbidden("Tenant não identificado. Verifique o domínio de acesso.")
        
        return None
