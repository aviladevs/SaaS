"""
Views para gestão de XMLs fiscais
Sistema mobile-first com design responsivo
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from .models import NFe, NFeItem, CTe, ImportLog
from datetime import datetime, timedelta


def login_view(request):
    """Login responsivo mobile-first"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal com estatísticas mobile-first"""
    
    # Período padrão: últimos 30 dias
    data_inicio = datetime.now() - timedelta(days=30)
    
    # Estatísticas NFe
    nfe_stats = {
        'total': NFe.objects.count(),
        'mes_atual': NFe.objects.filter(data_emissao__gte=data_inicio).count(),
        'valor_total': NFe.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
        'valor_mes': NFe.objects.filter(
            data_emissao__gte=data_inicio
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
    }
    
    # Estatísticas CTe
    cte_stats = {
        'total': CTe.objects.count(),
        'mes_atual': CTe.objects.filter(data_emissao__gte=data_inicio).count(),
        'valor_total': CTe.objects.aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
        'valor_mes': CTe.objects.filter(
            data_emissao__gte=data_inicio
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
    }
    
    # Últimas importações
    ultimos_logs = ImportLog.objects.select_related('usuario').order_by('-data_importacao')[:10]
    
    # Top 5 emitentes NFe
    top_emitentes = NFe.objects.values(
        'emit_cnpj', 'emit_nome'
    ).annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-total')[:5]
    
    # Últimas NFes
    ultimas_nfes = NFe.objects.select_related('usuario_importacao').order_by('-data_emissao')[:5]
    
    # Últimos CTes
    ultimos_ctes = CTe.objects.select_related('usuario_importacao').order_by('-data_emissao')[:5]
    
    context = {
        'nfe_stats': nfe_stats,
        'cte_stats': cte_stats,
        'ultimos_logs': ultimos_logs,
        'top_emitentes': top_emitentes,
        'ultimas_nfes': ultimas_nfes,
        'ultimos_ctes': ultimos_ctes,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def nfe_list(request):
    """Lista de NFes com filtros e paginação mobile-first"""
    
    # Filtros
    nfes = NFe.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        nfes = nfes.filter(
            Q(numero_nf__icontains=search) |
            Q(emit_nome__icontains=search) |
            Q(dest_nome__icontains=search) |
            Q(chave_acesso__icontains=search)
        )
    
    emit_cnpj = request.GET.get('emit_cnpj', '')
    if emit_cnpj:
        nfes = nfes.filter(emit_cnpj=emit_cnpj)
    
    data_inicio = request.GET.get('data_inicio', '')
    if data_inicio:
        nfes = nfes.filter(data_emissao__gte=data_inicio)
    
    data_fim = request.GET.get('data_fim', '')
    if data_fim:
        nfes = nfes.filter(data_emissao__lte=data_fim)
    
    # Ordenação
    ordem = request.GET.get('ordem', '-data_emissao')
    nfes = nfes.order_by(ordem)
    
    # Paginação
    paginator = Paginator(nfes, 20)
    page = request.GET.get('page', 1)
    nfes_page = paginator.get_page(page)
    
    # Totalizadores
    totais = nfes.aggregate(
        total_valor=Sum('valor_total'),
        total_produtos=Sum('valor_produtos'),
        total_icms=Sum('valor_icms')
    )
    
    context = {
        'nfes': nfes_page,
        'totais': totais,
        'search': search,
        'emit_cnpj': emit_cnpj,
    }
    
    return render(request, 'core/nfe_list.html', context)


@login_required
def nfe_detail(request, pk):
    """Detalhes de uma NFe mobile-first"""
    nfe = get_object_or_404(NFe, pk=pk)
    itens = nfe.itens.all()
    
    context = {
        'nfe': nfe,
        'itens': itens,
    }
    
    return render(request, 'core/nfe_detail.html', context)


@login_required
def cte_list(request):
    """Lista de CTes com filtros e paginação mobile-first"""
    
    # Filtros
    ctes = CTe.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        ctes = ctes.filter(
            Q(numero_ct__icontains=search) |
            Q(emit_nome__icontains=search) |
            Q(dest_nome__icontains=search) |
            Q(chave_acesso__icontains=search)
        )
    
    # Ordenação
    ordem = request.GET.get('ordem', '-data_emissao')
    ctes = ctes.order_by(ordem)
    
    # Paginação
    paginator = Paginator(ctes, 20)
    page = request.GET.get('page', 1)
    ctes_page = paginator.get_page(page)
    
    # Totalizadores
    totais = ctes.aggregate(
        total_valor=Sum('valor_total'),
        total_carga=Sum('valor_carga'),
        total_icms=Sum('valor_icms')
    )
    
    context = {
        'ctes': ctes_page,
        'totais': totais,
        'search': search,
    }
    
    return render(request, 'core/cte_list.html', context)


@login_required
def cte_detail(request, pk):
    """Detalhes de um CTe mobile-first"""
    cte = get_object_or_404(CTe, pk=pk)
    
    context = {
        'cte': cte,
    }
    
    return render(request, 'core/cte_detail.html', context)


@login_required
def import_logs(request):
    """Logs de importação mobile-first"""
    
    logs = ImportLog.objects.select_related('usuario').all()
    
    # Filtros
    tipo = request.GET.get('tipo', '')
    if tipo:
        logs = logs.filter(tipo_documento=tipo)
    
    status = request.GET.get('status', '')
    if status:
        logs = logs.filter(status=status)
    
    # Paginação
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    # Estatísticas
    stats = ImportLog.objects.values('tipo_documento', 'status').annotate(
        total=Count('id')
    )
    
    context = {
        'logs': logs_page,
        'stats': stats,
        'tipo_filter': tipo,
        'status_filter': status,
    }
    
    return render(request, 'core/import_logs.html', context)


@login_required
def analytics(request):
    """Análises e relatórios mobile-first"""
    
    # Vendas por mês (NFe)
    from django.db.models.functions import TruncMonth
    
    vendas_mes = NFe.objects.annotate(
        mes=TruncMonth('data_emissao')
    ).values('mes').annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-mes')[:12]
    
    # Top produtos (mais vendidos)
    top_produtos = NFeItem.objects.values(
        'codigo_produto', 'descricao'
    ).annotate(
        qtd_total=Sum('quantidade'),
        valor_total=Sum('valor_total')
    ).order_by('-qtd_total')[:10]
    
    # Rotas mais usadas (CTe)
    top_rotas = CTe.objects.values(
        'municipio_inicio', 'uf_inicio', 'municipio_fim', 'uf_fim'
    ).annotate(
        total=Count('id'),
        valor=Sum('valor_total')
    ).order_by('-total')[:10]
    
    context = {
        'vendas_mes': vendas_mes,
        'top_produtos': top_produtos,
        'top_rotas': top_rotas,
    }
    
    return render(request, 'core/analytics.html', context)
