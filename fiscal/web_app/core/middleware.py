"""
Middleware para logging e monitoramento de requisições API
"""
import time
import json
import logging
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)


class APIRequestLog(models.Model):
    """Log de requisições API"""
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    path = models.CharField(max_length=500, db_index=True)
    query_params = models.TextField(blank=True)
    
    status_code = models.IntegerField()
    response_time = models.FloatField(help_text="Tempo de resposta em segundos")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Para debug
    request_body = models.TextField(blank=True)
    response_body = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Log de Requisição API"
        verbose_name_plural = "Logs de Requisições API"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['path', '-timestamp']),
            models.Index(fields=['status_code']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.response_time:.3f}s)"


class APIRequestLoggingMiddleware:
    """
    Middleware para logging de requisições API
    
    Registra todas as requisições para /api/ com:
    - Método HTTP
    - Caminho
    - Parâmetros
    - Tempo de resposta
    - Status code
    - IP do cliente
    - User agent
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ignora requisições não-API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Marca tempo de início
        start_time = time.time()
        
        # Captura informações da requisição
        request_data = self._get_request_data(request)
        
        # Processa requisição
        response = self.get_response(request)
        
        # Calcula tempo de resposta
        response_time = time.time() - start_time
        
        # Registra log (assíncrono para não impactar performance)
        try:
            self._log_request(request, response, response_time, request_data)
        except Exception as e:
            logger.error(f"Erro ao registrar log de API: {str(e)}")
        
        # Adiciona headers de performance
        response['X-Response-Time'] = f"{response_time:.3f}s"
        
        return response
    
    def _get_request_data(self, request):
        """Extrai dados da requisição"""
        data = {}
        
        # Body da requisição (apenas para POST/PUT/PATCH)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    data['body'] = request.body.decode('utf-8')[:1000]  # Limita a 1000 caracteres
            except:
                pass
        
        return data
    
    def _log_request(self, request, response, response_time, request_data):
        """Registra log da requisição"""
        
        # Extrai usuário
        user = None
        if request.user and request.user.is_authenticated:
            user = request.user.username
        
        # IP do cliente
        ip_address = self._get_client_ip(request)
        
        # Cria log
        APIRequestLog.objects.create(
            user=user,
            method=request.method,
            path=request.path,
            query_params=json.dumps(dict(request.GET)),
            status_code=response.status_code,
            response_time=response_time,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_body=request_data.get('body', ''),
        )
        
        # Log no console também
        logger.info(
            f"API {request.method} {request.path} - "
            f"{response.status_code} - {response_time:.3f}s - "
            f"user={user or 'anonymous'}"
        )
    
    def _get_client_ip(self, request):
        """Obtém IP real do cliente (considerando proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware:
    """
    Middleware para rate limiting
    Limita número de requisições por IP/usuário
    """
    
    # Configurações
    RATE_LIMIT = 100  # requisições
    RATE_WINDOW = 60  # segundos
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}  # Cache em memória (em produção use Redis)
    
    def __call__(self, request):
        # Ignora requisições não-API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Identifica cliente
        client_id = self._get_client_id(request)
        
        # Verifica rate limit
        if self._is_rate_limited(client_id):
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'detail': f'Máximo de {self.RATE_LIMIT} requisições por {self.RATE_WINDOW} segundos'
            }, status=429)
        
        # Incrementa contador
        self._increment_count(client_id)
        
        # Processa requisição
        response = self.get_response(request)
        
        # Adiciona headers de rate limit
        remaining = self._get_remaining(client_id)
        response['X-RateLimit-Limit'] = str(self.RATE_LIMIT)
        response['X-RateLimit-Remaining'] = str(remaining)
        
        return response
    
    def _get_client_id(self, request):
        """Identifica cliente (usuário ou IP)"""
        if request.user and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Usa IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return f"ip:{ip}"
    
    def _is_rate_limited(self, client_id):
        """Verifica se cliente excedeu limite"""
        now = time.time()
        
        if client_id not in self.request_counts:
            return False
        
        # Remove requisições antigas
        self.request_counts[client_id] = [
            timestamp for timestamp in self.request_counts[client_id]
            if now - timestamp < self.RATE_WINDOW
        ]
        
        return len(self.request_counts[client_id]) >= self.RATE_LIMIT
    
    def _increment_count(self, client_id):
        """Incrementa contador de requisições"""
        now = time.time()
        
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        
        self.request_counts[client_id].append(now)
    
    def _get_remaining(self, client_id):
        """Retorna número de requisições restantes"""
        if client_id not in self.request_counts:
            return self.RATE_LIMIT
        
        return max(0, self.RATE_LIMIT - len(self.request_counts[client_id]))
