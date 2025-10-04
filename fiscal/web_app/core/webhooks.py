"""
Sistema de Webhooks para notificações automáticas
Permite que sistemas externos recebam notificações de eventos
"""
import requests
import json
import logging
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)


class Webhook(models.Model):
    """
    Configuração de webhook para notificações automáticas
    """
    
    EVENTO_CHOICES = [
        ('nfe_importada', 'NFe Importada'),
        ('cte_importado', 'CTe Importado'),
        ('consulta_concluida', 'Consulta SEFAZ Concluída'),
        ('documento_atualizado', 'Documento Atualizado'),
        ('erro_importacao', 'Erro na Importação'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    nome = models.CharField(max_length=200, help_text="Nome identificador do webhook")
    url = models.URLField(help_text="URL que receberá as notificações POST")
    eventos = models.CharField(
        max_length=500,
        help_text="Eventos separados por vírgula (ex: nfe_importada,cte_importado)"
    )
    
    # Segurança
    ativo = models.BooleanField(default=True)
    secret_key = models.CharField(
        max_length=100,
        blank=True,
        help_text="Chave secreta para validação HMAC (opcional)"
    )
    
    # Headers customizados (JSON)
    headers_customizados = models.TextField(
        blank=True,
        help_text="Headers HTTP customizados em formato JSON"
    )
    
    # Configurações
    timeout = models.IntegerField(default=30, help_text="Timeout em segundos")
    retry_count = models.IntegerField(default=3, help_text="Número de tentativas em caso de falha")
    
    # Auditoria
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ultima_execucao = models.DateTimeField(null=True, blank=True)
    total_execucoes = models.IntegerField(default=0)
    total_erros = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} - {self.url}"
    
    def get_eventos_list(self):
        """Retorna lista de eventos"""
        return [e.strip() for e in self.eventos.split(',') if e.strip()]
    
    def get_headers(self):
        """Retorna headers customizados"""
        if self.headers_customizados:
            try:
                return json.loads(self.headers_customizados)
            except json.JSONDecodeError:
                logger.error(f"Erro ao parsear headers do webhook {self.id}")
                return {}
        return {}
    
    def enviar(self, evento, dados):
        """
        Envia notificação do webhook
        
        Args:
            evento: Nome do evento
            dados: Dicionário com dados do evento
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self.ativo:
            return False
        
        if evento not in self.get_eventos_list():
            return False
        
        payload = {
            'evento': evento,
            'timestamp': timezone.now().isoformat(),
            'dados': dados
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'FiscalWebhook/1.0'
        }
        
        # Adiciona headers customizados
        headers.update(self.get_headers())
        
        # Adiciona assinatura HMAC se tiver secret_key
        if self.secret_key:
            import hmac
            import hashlib
            payload_json = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = signature
        
        # Tenta enviar com retries
        for tentativa in range(self.retry_count):
            try:
                response = requests.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                self.ultima_execucao = timezone.now()
                self.total_execucoes += 1
                
                if response.status_code >= 200 and response.status_code < 300:
                    self.save(update_fields=['ultima_execucao', 'total_execucoes'])
                    
                    # Registra log de sucesso
                    WebhookLog.objects.create(
                        webhook=self,
                        evento=evento,
                        status_code=response.status_code,
                        sucesso=True,
                        payload=json.dumps(payload),
                        response=response.text[:1000]
                    )
                    return True
                else:
                    raise Exception(f"Status code {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Erro ao enviar webhook {self.id} (tentativa {tentativa + 1}): {str(e)}")
                
                if tentativa == self.retry_count - 1:
                    # Última tentativa falhou
                    self.total_erros += 1
                    self.ultima_execucao = timezone.now()
                    self.save(update_fields=['ultima_execucao', 'total_erros'])
                    
                    # Registra log de erro
                    WebhookLog.objects.create(
                        webhook=self,
                        evento=evento,
                        status_code=0,
                        sucesso=False,
                        payload=json.dumps(payload),
                        erro=str(e)
                    )
        
        return False


class WebhookLog(models.Model):
    """Log de execuções de webhooks"""
    
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='logs')
    evento = models.CharField(max_length=50)
    data_execucao = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=False)
    status_code = models.IntegerField(default=0)
    payload = models.TextField()
    response = models.TextField(blank=True)
    erro = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Log de Webhook"
        verbose_name_plural = "Logs de Webhooks"
        ordering = ['-data_execucao']
    
    def __str__(self):
        status = "✓" if self.sucesso else "✗"
        return f"{status} {self.webhook.nome} - {self.evento} - {self.data_execucao}"


def disparar_webhook(evento, dados, usuario=None):
    """
    Dispara webhooks para um evento específico
    
    Args:
        evento: Nome do evento
        dados: Dicionário com dados do evento
        usuario: Usuário específico ou None para todos
    """
    if usuario:
        webhooks = Webhook.objects.filter(usuario=usuario, ativo=True)
    else:
        webhooks = Webhook.objects.filter(ativo=True)
    
    for webhook in webhooks:
        if evento in webhook.get_eventos_list():
            try:
                webhook.enviar(evento, dados)
            except Exception as e:
                logger.error(f"Erro ao disparar webhook {webhook.id}: {str(e)}")
