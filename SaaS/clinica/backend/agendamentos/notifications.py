"""
Sistema de Notificações para Agendamentos
Notificações via WhatsApp, email e push notifications
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import timedelta
import requests
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço centralizado de notificações"""

    def __init__(self):
        self.whatsapp_api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        self.whatsapp_token = getattr(settings, 'WHATSAPP_TOKEN', None)

    def enviar_confirmacao_agendamento(self, agendamento):
        """Envia confirmação de agendamento por múltiplos canais"""
        try:
            # Email
            if agendamento.cliente.email:
                self._enviar_email_confirmacao(agendamento)
            
            # WhatsApp
            if self.whatsapp_api_url and self.whatsapp_token:
                self._enviar_whatsapp_confirmacao(agendamento)
            
            logger.info(f"Notificação de confirmação enviada para agendamento {agendamento.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar confirmação: {e}")
            return False

    def enviar_lembrete_agendamento(self, agendamento, horas_antes=24):
        """Envia lembrete de agendamento"""
        try:
            # Verificar se é o momento certo para lembrete
            tempo_lembrete = agendamento.horario - timedelta(hours=horas_antes)
            if timezone.now() < tempo_lembrete:
                return False
            
            # Email
            if agendamento.cliente.email:
                self._enviar_email_lembrete(agendamento)
            
            # WhatsApp
            if self.whatsapp_api_url and self.whatsapp_token:
                self._enviar_whatsapp_lembrete(agendamento)
            
            logger.info(f"Lembrete enviado para agendamento {agendamento.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete: {e}")
            return False

    def enviar_cancelamento(self, agendamento):
        """Notifica cancelamento de agendamento"""
        try:
            # Email
            if agendamento.cliente.email:
                self._enviar_email_cancelamento(agendamento)
            
            # WhatsApp
            if self.whatsapp_api_url and self.whatsapp_token:
                self._enviar_whatsapp_cancelamento(agendamento)
            
            logger.info(f"Notificação de cancelamento enviada para agendamento {agendamento.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar cancelamento: {e}")
            return False

    def _enviar_email_confirmacao(self, agendamento):
        """Envia email de confirmação"""
        subject = f"Agendamento Confirmado - {agendamento.servico.nome}"
        
        context = {
            'agendamento': agendamento,
            'cliente': agendamento.cliente,
            'servico': agendamento.servico,
            'horario_formatado': agendamento.horario.strftime('%d/%m/%Y às %H:%M'),
        }
        
        html_message = render_to_string('emails/confirmacao_agendamento.html', context)
        plain_message = render_to_string('emails/confirmacao_agendamento.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[agendamento.cliente.email],
            html_message=html_message,
            fail_silently=False
        )

    def _enviar_email_lembrete(self, agendamento):
        """Envia email de lembrete"""
        subject = f"Lembrete: {agendamento.servico.nome} amanhã"
        
        context = {
            'agendamento': agendamento,
            'cliente': agendamento.cliente,
            'servico': agendamento.servico,
            'horario_formatado': agendamento.horario.strftime('%d/%m/%Y às %H:%M'),
        }
        
        html_message = render_to_string('emails/lembrete_agendamento.html', context)
        plain_message = render_to_string('emails/lembrete_agendamento.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[agendamento.cliente.email],
            html_message=html_message,
            fail_silently=False
        )

    def _enviar_email_cancelamento(self, agendamento):
        """Envia email de cancelamento"""
        subject = f"Agendamento Cancelado - {agendamento.servico.nome}"
        
        context = {
            'agendamento': agendamento,
            'cliente': agendamento.cliente,
            'servico': agendamento.servico,
            'horario_formatado': agendamento.horario.strftime('%d/%m/%Y às %H:%M'),
        }
        
        html_message = render_to_string('emails/cancelamento_agendamento.html', context)
        plain_message = render_to_string('emails/cancelamento_agendamento.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[agendamento.cliente.email],
            html_message=html_message,
            fail_silently=False
        )

    def _enviar_whatsapp_confirmacao(self, agendamento):
        """Envia WhatsApp de confirmação"""
        mensagem = f"""
✅ *Agendamento Confirmado*

Olá {agendamento.cliente.nome}!

Seu agendamento foi confirmado:
📅 *Serviço:* {agendamento.servico.nome}
🕐 *Data/Hora:* {agendamento.horario.strftime('%d/%m/%Y às %H:%M')}
💰 *Valor:* R$ {agendamento.valor_cobrado}

📍 *Endereço:* [Inserir endereço]

Estaremos te esperando! 😊
        """.strip()
        
        self._enviar_whatsapp(agendamento.cliente.whatsapp, mensagem)

    def _enviar_whatsapp_lembrete(self, agendamento):
        """Envia WhatsApp de lembrete"""
        mensagem = f"""
🔔 *Lembrete de Agendamento*

Olá {agendamento.cliente.nome}!

Lembramos que você tem um agendamento:
📅 *Serviço:* {agendamento.servico.nome}
🕐 *Amanhã às:* {agendamento.horario.strftime('%H:%M')}

Aguardamos você! 💆‍♀️
        """.strip()
        
        self._enviar_whatsapp(agendamento.cliente.whatsapp, mensagem)

    def _enviar_whatsapp_cancelamento(self, agendamento):
        """Envia WhatsApp de cancelamento"""
        mensagem = f"""
❌ *Agendamento Cancelado*

Olá {agendamento.cliente.nome}!

Seu agendamento foi cancelado:
📅 *Serviço:* {agendamento.servico.nome}
🕐 *Data/Hora:* {agendamento.horario.strftime('%d/%m/%Y às %H:%M')}

Para reagendar, entre em contato conosco.
        """.strip()
        
        self._enviar_whatsapp(agendamento.cliente.whatsapp, mensagem)

    def _enviar_whatsapp(self, numero, mensagem):
        """Envia mensagem via API do WhatsApp"""
        if not self.whatsapp_api_url or not self.whatsapp_token:
            logger.warning("WhatsApp API não configurada")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': numero.replace('+', '').replace(' ', ''),
                'type': 'text',
                'text': {
                    'body': mensagem
                }
            }
            
            response = requests.post(
                f"{self.whatsapp_api_url}/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp enviado para {numero}")
                return True
            else:
                logger.error(f"Erro WhatsApp API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return False


# Funções de conveniência
def enviar_confirmacao_agendamento(agendamento):
    """Função de conveniência para enviar confirmação"""
    service = NotificationService()
    return service.enviar_confirmacao_agendamento(agendamento)


def enviar_lembrete_agendamento(agendamento, horas_antes=24):
    """Função de conveniência para enviar lembrete"""
    service = NotificationService()
    return service.enviar_lembrete_agendamento(agendamento, horas_antes)


def enviar_cancelamento_agendamento(agendamento):
    """Função de conveniência para enviar cancelamento"""
    service = NotificationService()
    return service.enviar_cancelamento(agendamento)


# Tarefa Celery para processamento assíncrono
from celery import shared_task

@shared_task
def processar_lembretes_agendamentos():
    """Tarefa para processar lembretes de agendamentos"""
    from .models import Agendamento
    
    # Agendamentos que precisam de lembrete (24h antes)
    agora = timezone.now()
    inicio_janela = agora + timedelta(hours=23, minutes=30)
    fim_janela = agora + timedelta(hours=24, minutes=30)
    
    agendamentos_lembrete = Agendamento.objects.filter(
        horario__gte=inicio_janela,
        horario__lte=fim_janela,
        status='confirmado'
    )
    
    service = NotificationService()
    count = 0
    
    for agendamento in agendamentos_lembrete:
        if service.enviar_lembrete_agendamento(agendamento):
            count += 1
    
    logger.info(f"Processados {count} lembretes de agendamento")
    return count


@shared_task
def processar_agendamentos_atrasados():
    """Tarefa para identificar e notificar agendamentos atrasados"""
    from .models import Agendamento
    
    agora = timezone.now()
    agendamentos_atrasados = Agendamento.objects.filter(
        horario__lt=agora - timedelta(minutes=15),
        status='confirmado'
    )
    
    count = 0
    for agendamento in agendamentos_atrasados:
        # Marcar como perdido
        agendamento.status = 'falta'
        agendamento.observacoes += f"\nMarcado como falta automaticamente em {agora}"
        agendamento.save()
        count += 1
    
    logger.info(f"Processados {count} agendamentos atrasados")
    return count