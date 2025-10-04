"""
Middleware de Segurança Avançado
Implementa proteções adicionais além das padrão do Django
"""

import time
import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .throttling import BruteForceProtection, get_client_ip

logger = logging.getLogger('security')


class SecurityMiddleware(MiddlewareMixin):
    """Middleware para proteções de segurança adicionais"""

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """Processar request antes da view"""
        
        # Verificar proteção contra força bruta
        client_ip = get_client_ip(request)
        
        if not BruteForceProtection.check_failed_attempts(client_ip):
            logger.warning(f"IP blocked due to too many failed attempts: {client_ip}")
            return JsonResponse({
                'error': 'Too many failed attempts. Please try again later.',
                'code': 'RATE_LIMITED'
            }, status=429)
        
        # Verificar user-agent suspeito
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['curl', 'wget', 'python-requests', 'bot', 'crawler']
        
        if any(agent in user_agent for agent in suspicious_agents):
            # Log tentativa suspeita
            logger.warning(f"Suspicious user agent from {client_ip}: {user_agent}")
            
            # Aplicar rate limiting mais rigoroso para bots
            cache_key = f"bot_requests_{client_ip}"
            requests_count = cache.get(cache_key, 0)
            
            if requests_count > 10:  # Máximo 10 requests por minuto para bots
                return JsonResponse({
                    'error': 'Rate limit exceeded for automated requests',
                    'code': 'BOT_RATE_LIMITED'
                }, status=429)
            
            cache.set(cache_key, requests_count + 1, 60)  # Janela de 1 minuto

    def process_response(self, request, response):
        """Processar response antes de enviar"""
        
        # Adicionar headers de segurança adicionais
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Headers específicos para API
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware para log detalhado de requests"""

    def process_request(self, request):
        """Log informações do request"""
        request._start_time = time.time()
        
        # Log apenas requests importantes
        should_log = (
            request.method in ['POST', 'PUT', 'DELETE'] or
            request.path.startswith('/admin/') or
            request.path.startswith('/api/')
        )
        
        if should_log:
            client_ip = get_client_ip(request)
            user = getattr(request, 'user', None)
            user_id = user.id if user and user.is_authenticated else 'anonymous'
            
            logger.info(
                f"Request: {request.method} {request.path} | "
                f"IP: {client_ip} | User: {user_id} | "
                f"UA: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"
            )

    def process_response(self, request, response):
        """Log informações da response"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log responses com erro ou requests importantes
            should_log = (
                response.status_code >= 400 or
                duration > 1.0 or  # Requests lentos
                request.method in ['POST', 'PUT', 'DELETE']
            )
            
            if should_log:
                client_ip = get_client_ip(request)
                user = getattr(request, 'user', None)
                user_id = user.id if user and user.is_authenticated else 'anonymous'
                
                log_level = logging.ERROR if response.status_code >= 400 else logging.INFO
                logger.log(
                    log_level,
                    f"Response: {response.status_code} | "
                    f"Duration: {duration:.3f}s | "
                    f"Path: {request.path} | "
                    f"IP: {client_ip} | User: {user_id}"
                )
        
        return response


class CSPMiddleware(MiddlewareMixin):
    """Content Security Policy Middleware"""

    def process_response(self, request, response):
        """Adicionar CSP headers"""
        
        # CSP básico - ajustar conforme necessário
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' *.googleapis.com *.gstatic.com; "
            "style-src 'self' 'unsafe-inline' *.googleapis.com *.gstatic.com; "
            "img-src 'self' data: *.googleapis.com *.gstatic.com; "
            "font-src 'self' *.googleapis.com *.gstatic.com; "
            "connect-src 'self' *.googleapis.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "object-src 'none';"
        )
        
        response['Content-Security-Policy'] = csp
        
        # Report-only para desenvolvimento
        if settings.DEBUG:
            response['Content-Security-Policy-Report-Only'] = csp
            del response['Content-Security-Policy']
        
        return response