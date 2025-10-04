"""
API endpoints para gerenciamento de webhooks e integrações
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.utils import timezone

from core.webhooks import Webhook, WebhookLog, disparar_webhook
from .serializers import WebhookSerializer, WebhookLogSerializer


class WebhookViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de webhooks
    
    Endpoints:
    - GET /api/webhooks/ - Lista webhooks do usuário
    - POST /api/webhooks/ - Cria novo webhook
    - GET /api/webhooks/{id}/ - Detalhes de um webhook
    - PUT /api/webhooks/{id}/ - Atualiza webhook
    - DELETE /api/webhooks/{id}/ - Remove webhook
    - POST /api/webhooks/{id}/testar/ - Testa webhook
    - GET /api/webhooks/{id}/logs/ - Logs do webhook
    """
    
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas webhooks do usuário logado"""
        return Webhook.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """Associa webhook ao usuário logado"""
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def testar(self, request, pk=None):
        """Testa envio de webhook"""
        webhook = self.get_object()
        
        # Dados de teste
        dados_teste = {
            'tipo': 'teste',
            'mensagem': 'Este é um webhook de teste',
            'timestamp': timezone.now().isoformat(),
            'usuario': request.user.username
        }
        
        sucesso = webhook.enviar('nfe_importada', dados_teste)
        
        if sucesso:
            return Response({
                'status': 'success',
                'mensagem': 'Webhook enviado com sucesso'
            })
        else:
            return Response({
                'status': 'error',
                'mensagem': 'Falha ao enviar webhook. Verifique os logs.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Retorna logs do webhook"""
        webhook = self.get_object()
        logs = webhook.logs.all()[:50]  # Últimos 50 logs
        serializer = WebhookLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas de webhooks do usuário"""
        webhooks = self.get_queryset()
        
        total = webhooks.count()
        ativos = webhooks.filter(ativo=True).count()
        
        # Execuções nas últimas 24h
        ontem = timezone.now() - timedelta(hours=24)
        execucoes_24h = WebhookLog.objects.filter(
            webhook__usuario=request.user,
            data_execucao__gte=ontem
        ).count()
        
        # Taxa de sucesso
        logs_recentes = WebhookLog.objects.filter(
            webhook__usuario=request.user,
            data_execucao__gte=ontem
        )
        total_logs = logs_recentes.count()
        sucesso_logs = logs_recentes.filter(sucesso=True).count()
        taxa_sucesso = (sucesso_logs / total_logs * 100) if total_logs > 0 else 0
        
        return Response({
            'total_webhooks': total,
            'webhooks_ativos': ativos,
            'execucoes_24h': execucoes_24h,
            'taxa_sucesso': round(taxa_sucesso, 2),
            'total_logs': total_logs,
            'logs_sucesso': sucesso_logs
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def testar_integracao(request):
    """
    Endpoint para testar integração completa
    
    POST /api/integracoes/testar/
    
    Body:
    {
        "webhook_id": 123,
        "evento": "nfe_importada",
        "dados": {...}
    }
    """
    webhook_id = request.data.get('webhook_id')
    evento = request.data.get('evento', 'nfe_importada')
    dados = request.data.get('dados', {})
    
    if not webhook_id:
        return Response({
            'error': 'webhook_id é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        webhook = Webhook.objects.get(id=webhook_id, usuario=request.user)
        
        # Adiciona dados do usuário
        dados['usuario'] = request.user.username
        dados['timestamp'] = timezone.now().isoformat()
        dados['teste'] = True
        
        sucesso = webhook.enviar(evento, dados)
        
        if sucesso:
            return Response({
                'status': 'success',
                'mensagem': 'Integração testada com sucesso',
                'webhook': webhook.nome,
                'evento': evento
            })
        else:
            return Response({
                'status': 'error',
                'mensagem': 'Falha ao enviar webhook'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Webhook.DoesNotExist:
        return Response({
            'error': 'Webhook não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disparar_evento(request):
    """
    Endpoint para disparar manualmente um evento
    
    POST /api/integracoes/disparar/
    
    Body:
    {
        "evento": "nfe_importada",
        "dados": {...}
    }
    """
    evento = request.data.get('evento')
    dados = request.data.get('dados', {})
    
    if not evento:
        return Response({
            'error': 'evento é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Adiciona dados do usuário
    dados['usuario'] = request.user.username
    dados['timestamp'] = timezone.now().isoformat()
    dados['manual'] = True
    
    # Dispara webhooks
    disparar_webhook(evento, dados, usuario=request.user)
    
    # Conta quantos webhooks foram acionados
    webhooks_acionados = Webhook.objects.filter(
        usuario=request.user,
        ativo=True,
        eventos__contains=evento
    ).count()
    
    return Response({
        'status': 'success',
        'mensagem': f'Evento {evento} disparado',
        'webhooks_acionados': webhooks_acionados
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eventos_disponiveis(request):
    """
    Lista eventos disponíveis para webhooks
    
    GET /api/integracoes/eventos/
    """
    from core.webhooks import Webhook
    
    eventos = [
        {
            'id': choice[0],
            'nome': choice[1],
            'descricao': f'Disparado quando {choice[1].lower()}'
        }
        for choice in Webhook.EVENTO_CHOICES
    ]
    
    return Response({
        'eventos': eventos,
        'total': len(eventos)
    })
