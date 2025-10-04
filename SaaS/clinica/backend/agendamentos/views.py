from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from .models import Cliente, Servico, Agendamento
from .serializers import (
    ClienteSerializer, ServicoSerializer,
    AgendamentoCreateSerializer, AgendamentoDetailSerializer,
    AgendamentoUpdateSerializer, DashboardSerializer, CalendarioSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet completa para gerenciamento de clientes"""

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'whatsapp', 'email']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']

    @action(detail=True, methods=['get'])
    def agendamentos(self, request, pk=None):
        """Lista agendamentos de um cliente específico"""
        cliente = self.get_object()
        agendamentos = cliente.agendamento_set.all().order_by('-horario')

        # Filtros opcionais
        status_filter = request.query_params.get('status')
        if status_filter:
            agendamentos = agendamentos.filter(status=status_filter)

        # Paginação
        page = self.paginate_queryset(agendamentos)
        if page is not None:
            serializer = AgendamentoDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AgendamentoDetailSerializer(agendamentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """Histórico completo do cliente"""
        cliente = self.get_object()
        return Response({
            'cliente': ClienteSerializer(cliente).data,
            'total_agendamentos': cliente.total_agendamentos(),
            'agendamentos_por_status': cliente.agendamento_set.values('status').annotate(
                count=Count('id')
            ),
            'valor_total_pago': cliente.agendamento_set.filter(
                status='concluido'
            ).aggregate(total=Sum('valor_cobrado'))['total'] or 0,
            'ultimo_agendamento': cliente.ultimo_agendamento()
        })


class ServicoViewSet(viewsets.ModelViewSet):
    """ViewSet completa para gerenciamento de serviços"""

    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'valor', 'duracao_minutos']
    ordering = ['nome']

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Estatísticas dos serviços"""
        hoje = timezone.now()
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stats = []
        for servico in self.get_queryset():
            agendamentos_mes = servico.agendamento_set.filter(
                horario__gte=inicio_mes,
                status__in=['confirmado', 'concluido']
            )

            stats.append({
                'servico': ServicoSerializer(servico).data,
                'agendamentos_mes': agendamentos_mes.count(),
                'receita_mes': agendamentos_mes.filter(
                    status='concluido'
                ).aggregate(total=Sum('valor_cobrado'))['total'] or 0,
                'taxa_conclusao': self._calcular_taxa_conclusao(servico, inicio_mes)
            })

        return Response(stats)

    def _calcular_taxa_conclusao(self, servico, inicio_periodo):
        """Calcula taxa de conclusão do serviço"""
        total = servico.agendamento_set.filter(
            horario__gte=inicio_periodo,
            horario__lt=timezone.now()
        ).count()

        if total == 0:
            return 0

        concluidos = servico.agendamento_set.filter(
            horario__gte=inicio_periodo,
            horario__lt=timezone.now(),
            status='concluido'
        ).count()

        return round((concluidos / total) * 100, 2)


class AgendamentoViewSet(viewsets.ModelViewSet):
    """ViewSet completa para gerenciamento de agendamentos"""

    queryset = Agendamento.objects.select_related('cliente', 'servico').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'cliente', 'servico']
    search_fields = ['cliente__nome', 'servico__nome', 'observacoes']
    ordering_fields = ['horario', 'criado_em']
    ordering = ['-horario']

    def get_serializer_class(self):
        """Serializer específico por ação"""
        if self.action == 'create':
            return AgendamentoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AgendamentoUpdateSerializer
        else:
            return AgendamentoDetailSerializer

    def get_queryset(self):
        """Queryset com filtros específicos"""
        queryset = super().get_queryset()

        # Filtro por data
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio:
            queryset = queryset.filter(horario__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(horario__lte=data_fim)

        # Filtro para agendamentos de hoje
        if self.request.query_params.get('hoje'):
            hoje = timezone.now().date()
            queryset = queryset.filter(horario__date=hoje)

        # Filtro para agendamentos atrasados
        if self.request.query_params.get('atrasados'):
            agora = timezone.now()
            queryset = queryset.filter(
                horario__lt=agora,
                status='confirmado'
            )

        return queryset

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dados para dashboard principal"""
        hoje = timezone.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Agendamentos
        agendamentos_hoje = Agendamento.objects.filter(
            horario__date=hoje.date()
        ).count()

        agendamentos_semana = Agendamento.objects.filter(
            horario__gte=inicio_semana
        ).count()

        agendamentos_mes = Agendamento.objects.filter(
            horario__gte=inicio_mes
        ).count()

        # Receita do mês
        receita_mes = Agendamento.objects.filter(
            horario__gte=inicio_mes,
            status='concluido'
        ).aggregate(total=Sum('valor_cobrado'))['total'] or 0

        # Clientes ativos
        clientes_ativos = Cliente.objects.filter(ativo=True).count()

        # Serviços mais procurados
        servicos_populares = Servico.objects.annotate(
            total_agendamentos=Count('agendamento')
        ).order_by('-total_agendamentos')[:5]

        servicos_mais_procurados = [
            {
                'nome': s.nome,
                'total': s.total_agendamentos,
                'valor': float(s.valor)
            }
            for s in servicos_populares
        ]

        # Próximos agendamentos
        proximos = Agendamento.objects.filter(
            horario__gte=hoje,
            status='confirmado'
        ).order_by('horario')[:10]

        data = {
            'agendamentos_hoje': agendamentos_hoje,
            'agendamentos_semana': agendamentos_semana,
            'agendamentos_mes': agendamentos_mes,
            'receita_mes': receita_mes,
            'clientes_ativos': clientes_ativos,
            'servicos_mais_procurados': servicos_mais_procurados,
            'proximos_agendamentos': AgendamentoDetailSerializer(proximos, many=True).data
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def calendario(self, request):
        """Dados para visualização em calendário"""
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        queryset = self.get_queryset()

        if start:
            queryset = queryset.filter(horario__gte=start)
        if end:
            queryset = queryset.filter(horario__lte=end)

        eventos = []
        for agendamento in queryset:
            eventos.append({
                'id': agendamento.id,
                'title': f"{agendamento.cliente.nome} - {agendamento.servico.nome}",
                'start': agendamento.horario,
                'end': agendamento.horario_fim,
                'color': agendamento.servico.cor_calendario,
                'cliente': agendamento.cliente.nome,
                'servico': agendamento.servico.nome,
                'status': agendamento.status,
                'observacoes': agendamento.observacoes or ''
            })

        serializer = CalendarioSerializer(eventos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar agendamento"""
        agendamento = self.get_object()

        if not agendamento.pode_cancelar:
            return Response(
                {'error': 'Agendamento não pode ser cancelado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        agendamento.status = 'cancelado'
        agendamento.observacoes += f"\nCancelado em {timezone.now()}"
        agendamento.save()

        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """Marcar agendamento como concluído"""
        agendamento = self.get_object()

        if agendamento.status != 'confirmado':
            return Response(
                {'error': 'Apenas agendamentos confirmados podem ser concluídos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        agendamento.status = 'concluido'

        # Observações do atendimento
        observacoes_atendimento = request.data.get('observacoes', '')
        if observacoes_atendimento:
            agendamento.observacoes += f"\nAtendimento: {observacoes_atendimento}"

        agendamento.save()

        serializer = self.get_serializer(agendamento)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def relatorio(self, request):
        """Relatório de agendamentos"""
        # Parâmetros de filtro
        inicio = request.query_params.get('inicio', timezone.now().replace(day=1).date())
        fim = request.query_params.get('fim', timezone.now().date())

        agendamentos = Agendamento.objects.filter(
            horario__date__gte=inicio,
            horario__date__lte=fim
        )

        # Estatísticas
        total_agendamentos = agendamentos.count()
        por_status = agendamentos.values('status').annotate(count=Count('id'))
        receita_total = agendamentos.filter(
            status='concluido'
        ).aggregate(total=Sum('valor_cobrado'))['total'] or 0

        # Top clientes
        top_clientes = agendamentos.values(
            'cliente__nome'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        # Top serviços
        top_servicos = agendamentos.values(
            'servico__nome'
        ).annotate(
            total=Count('id'),
            receita=Sum('valor_cobrado')
        ).order_by('-total')[:10]

        return Response({
            'periodo': {'inicio': inicio, 'fim': fim},
            'total_agendamentos': total_agendamentos,
            'por_status': list(por_status),
            'receita_total': receita_total,
            'top_clientes': list(top_clientes),
            'top_servicos': list(top_servicos)
        })
