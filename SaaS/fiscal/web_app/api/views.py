"""
API REST Views para App Mobile
Endpoints otimizados para consumo mobile
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from core.models import NFe, NFeItem, CTe, ImportLog
from .serializers import (
    NFeListSerializer, NFeDetailSerializer,
    CTeListSerializer, CTeDetailSerializer,
    ImportLogSerializer, DashboardSerializer,
    StatisticsSerializer
)


class NFeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para NFes
    
    Endpoints:
    - GET /api/nfe/ - Lista todas as NFes
    - GET /api/nfe/{id}/ - Detalhes de uma NFe
    - GET /api/nfe/search/?q=termo - Busca por termo
    - GET /api/nfe/by_emitente/?cnpj=00000000000000 - Filtra por emitente
    """
    
    queryset = NFe.objects.all().order_by('-data_emissao')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_nf', 'emit_nome', 'dest_nome', 'chave_acesso']
    ordering_fields = ['data_emissao', 'valor_total', 'numero_nf']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NFeDetailSerializer
        return NFeListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por CNPJ emitente
        cnpj = self.request.query_params.get('cnpj', None)
        if cnpj:
            queryset = queryset.filter(emit_cnpj=cnpj)
        
        # Filtro por período
        data_inicio = self.request.query_params.get('data_inicio', None)
        if data_inicio:
            queryset = queryset.filter(data_emissao__gte=data_inicio)
        
        data_fim = self.request.query_params.get('data_fim', None)
        if data_fim:
            queryset = queryset.filter(data_emissao__lte=data_fim)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def totais(self, request):
        """Retorna totalizadores das NFes"""
        queryset = self.filter_queryset(self.get_queryset())
        
        totais = queryset.aggregate(
            total_notas=Count('id'),
            valor_total=Sum('valor_total'),
            valor_produtos=Sum('valor_produtos'),
            valor_icms=Sum('valor_icms'),
            valor_ipi=Sum('valor_ipi')
        )
        
        return Response(totais)
    
    @action(detail=False, methods=['get'])
    def por_emitente(self, request):
        """Agrupa NFes por emitente"""
        queryset = self.filter_queryset(self.get_queryset())
        
        emitentes = queryset.values(
            'emit_cnpj', 'emit_nome'
        ).annotate(
            total_notas=Count('id'),
            valor_total=Sum('valor_total')
        ).order_by('-total_notas')[:20]
        
        return Response(emitentes)


class CTeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para CTes
    
    Endpoints:
    - GET /api/cte/ - Lista todos os CTes
    - GET /api/cte/{id}/ - Detalhes de um CTe
    - GET /api/cte/search/?q=termo - Busca por termo
    """
    
    queryset = CTe.objects.all().order_by('-data_emissao')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_ct', 'emit_nome', 'dest_nome', 'chave_acesso']
    ordering_fields = ['data_emissao', 'valor_total', 'numero_ct']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CTeDetailSerializer
        return CTeListSerializer
    
    @action(detail=False, methods=['get'])
    def totais(self, request):
        """Retorna totalizadores dos CTes"""
        queryset = self.filter_queryset(self.get_queryset())
        
        totais = queryset.aggregate(
            total_ctes=Count('id'),
            valor_total=Sum('valor_total'),
            valor_carga=Sum('valor_carga'),
            valor_icms=Sum('valor_icms')
        )
        
        return Response(totais)
    
    @action(detail=False, methods=['get'])
    def rotas(self, request):
        """Agrupa CTes por rota"""
        queryset = self.filter_queryset(self.get_queryset())
        
        rotas = queryset.values(
            'municipio_inicio', 'uf_inicio',
            'municipio_fim', 'uf_fim'
        ).annotate(
            total_ctes=Count('id'),
            valor_total=Sum('valor_total')
        ).order_by('-total_ctes')[:20]
        
        return Response(rotas)


class ImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para logs de importação
    
    Endpoints:
    - GET /api/logs/ - Lista logs
    - GET /api/logs/{id}/ - Detalhes de um log
    """
    
    queryset = ImportLog.objects.all().order_by('-data_importacao')
    serializer_class = ImportLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo_documento=tipo)
        
        # Filtro por status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    """
    Endpoint para dados do dashboard mobile
    
    GET /api/dashboard/
    
    Retorna estatísticas gerais do sistema
    """
    
    # Período: últimos 30 dias
    data_inicio = datetime.now() - timedelta(days=30)
    
    # Estatísticas NFe
    nfe_total = NFe.objects.count()
    nfe_mes = NFe.objects.filter(data_emissao__gte=data_inicio).count()
    nfe_valor_total = NFe.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    nfe_valor_mes = NFe.objects.filter(
        data_emissao__gte=data_inicio
    ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    # Estatísticas CTe
    cte_total = CTe.objects.count()
    cte_mes = CTe.objects.filter(data_emissao__gte=data_inicio).count()
    cte_valor_total = CTe.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    cte_valor_mes = CTe.objects.filter(
        data_emissao__gte=data_inicio
    ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    
    # Últimos logs
    ultimos_logs = ImportLog.objects.order_by('-data_importacao')[:10]
    
    data = {
        'nfe_total': nfe_total,
        'nfe_mes': nfe_mes,
        'nfe_valor_total': nfe_valor_total,
        'nfe_valor_mes': nfe_valor_mes,
        'cte_total': cte_total,
        'cte_mes': cte_mes,
        'cte_valor_total': cte_valor_total,
        'cte_valor_mes': cte_valor_mes,
        'ultimos_logs': ImportLogSerializer(ultimos_logs, many=True).data,
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_api(request):
    """
    Endpoint para estatísticas e análises
    
    GET /api/statistics/
    
    Retorna análises detalhadas para dashboard mobile
    """
    
    # Top 10 emitentes
    top_emitentes = list(NFe.objects.values(
        'emit_cnpj', 'emit_nome'
    ).annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-total')[:10])
    
    # Top 10 produtos
    top_produtos = list(NFeItem.objects.values(
        'codigo_produto', 'descricao'
    ).annotate(
        qtd_total=Sum('quantidade'),
        valor_total=Sum('valor_total')
    ).order_by('-qtd_total')[:10])
    
    # Top 10 rotas
    top_rotas = list(CTe.objects.values(
        'municipio_inicio', 'uf_inicio',
        'municipio_fim', 'uf_fim'
    ).annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-total')[:10])
    
    # Vendas por mês (últimos 12 meses)
    vendas_por_mes = list(NFe.objects.annotate(
        mes=TruncMonth('data_emissao')
    ).values('mes').annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-mes')[:12])
    
    data = {
        'top_emitentes': top_emitentes,
        'top_produtos': top_produtos,
        'top_rotas': top_rotas,
        'vendas_por_mes': vendas_por_mes,
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_api(request):
    """
    Busca unificada em NFes e CTes
    
    GET /api/search/?q=termo
    
    Busca em múltiplos campos de NFes e CTes
    """
    
    query = request.GET.get('q', '')
    
    if not query:
        return Response({'error': 'Parâmetro q é obrigatório'}, status=400)
    
    # Busca em NFes
    nfes = NFe.objects.filter(
        Q(numero_nf__icontains=query) |
        Q(chave_acesso__icontains=query) |
        Q(emit_nome__icontains=query) |
        Q(dest_nome__icontains=query)
    ).order_by('-data_emissao')[:20]
    
    # Busca em CTes
    ctes = CTe.objects.filter(
        Q(numero_ct__icontains=query) |
        Q(chave_acesso__icontains=query) |
        Q(emit_nome__icontains=query) |
        Q(dest_nome__icontains=query)
    ).order_by('-data_emissao')[:20]
    
    data = {
        'nfes': NFeListSerializer(nfes, many=True).data,
        'ctes': CTeListSerializer(ctes, many=True).data,
        'total_results': nfes.count() + ctes.count(),
    }
    
    return Response(data)
