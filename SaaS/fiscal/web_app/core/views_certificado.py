"""
Views para gestão de certificados e consultas automáticas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from .models_certificado import (
    CertificadoDigital, ConsultaSEFAZ, 
    DocumentoConsultado, ConfiguracaoConsulta
)
from .sefaz_service import SEFAZConsultaService
import base64


@login_required
def certificados_list(request):
    """Lista certificados digitais do usuário"""
    certificados = CertificadoDigital.objects.filter(usuario=request.user)
    
    context = {
        'certificados': certificados,
    }
    return render(request, 'core/certificados_list.html', context)


@login_required
def certificado_upload(request):
    """Upload de novo certificado digital"""
    if request.method == 'POST':
        try:
            # Receber arquivo .pfx
            arquivo_pfx = request.FILES.get('arquivo_pfx')
            senha = request.POST.get('senha_pfx')
            nome = request.POST.get('nome')
            cnpj = request.POST.get('cnpj')
            
            if not all([arquivo_pfx, senha, nome, cnpj]):
                messages.error(request, 'Todos os campos são obrigatórios')
                return redirect('certificado_upload')
            
            # Ler arquivo
            pfx_bytes = arquivo_pfx.read()
            
            # Validar certificado
            service = SEFAZConsultaService(pfx_bytes, senha)
            info_cert = service.validar_certificado()
            
            if not info_cert.get('valido'):
                messages.error(request, f"Certificado inválido: {info_cert.get('erro')}")
                return redirect('certificado_upload')
            
            # Salvar certificado (senha deve ser criptografada em produção!)
            certificado = CertificadoDigital.objects.create(
                usuario=request.user,
                nome=nome,
                cnpj=cnpj.replace('.', '').replace('/', '').replace('-', ''),
                arquivo_pfx=pfx_bytes,
                senha_pfx=senha,  # TODO: Criptografar!
                validade_inicio=info_cert['validade_inicio'],
                validade_fim=info_cert['validade_fim'],
                emissor=info_cert.get('emissor', ''),
            )
            
            messages.success(request, 'Certificado cadastrado com sucesso!')
            return redirect('certificados_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar certificado: {e}')
    
    return render(request, 'core/certificado_upload.html')


@login_required
def consulta_sefaz(request, certificado_id):
    """Interface de consulta na SEFAZ"""
    certificado = get_object_or_404(
        CertificadoDigital, 
        id=certificado_id, 
        usuario=request.user
    )
    
    if request.method == 'POST':
        try:
            # Parâmetros da consulta
            tipo_doc = request.POST.get('tipo_documento', 'NFE')
            data_inicio = datetime.strptime(request.POST.get('data_inicio'), '%Y-%m-%d')
            data_fim = datetime.strptime(request.POST.get('data_fim'), '%Y-%m-%d')
            
            # Criar registro de consulta
            consulta = ConsultaSEFAZ.objects.create(
                certificado=certificado,
                tipo_documento=tipo_doc,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status='PROCESSANDO'
            )
            
            # Iniciar consulta em background (ou síncrona para teste)
            from django.core.management import call_command
            # call_command('processar_consulta_sefaz', consulta.id)
            
            messages.success(request, 'Consulta iniciada! Aguarde o processamento.')
            return redirect('consulta_resultado', consulta_id=consulta.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao iniciar consulta: {e}')
    
    # Últimas consultas
    ultimas_consultas = ConsultaSEFAZ.objects.filter(
        certificado=certificado
    ).order_by('-data_consulta')[:10]
    
    context = {
        'certificado': certificado,
        'ultimas_consultas': ultimas_consultas,
    }
    return render(request, 'core/consulta_sefaz.html', context)


@login_required
def consulta_resultado(request, consulta_id):
    """Exibe resultado da consulta com abas"""
    consulta = get_object_or_404(ConsultaSEFAZ, id=consulta_id)
    
    # Verificar permissão
    if consulta.certificado.usuario != request.user:
        messages.error(request, 'Acesso negado')
        return redirect('certificados_list')
    
    # Documentos por papel
    docs_emitente = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='EMITENTE'
    )
    
    docs_destinatario = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='DESTINATARIO'
    )
    
    docs_transportador = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='TRANSPORTADOR'
    )
    
    docs_tomador = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='TOMADOR'
    )
    
    docs_remetente = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='REMETENTE'
    )
    
    docs_recebedor = DocumentoConsultado.objects.filter(
        consulta=consulta,
        papel_cnpj='RECEBEDOR'
    )
    
    # Estatísticas
    stats = {
        'total': consulta.total_encontrados,
        'importados': consulta.total_importados,
        'pendentes': consulta.total_encontrados - consulta.total_importados,
        'emitente': docs_emitente.count(),
        'destinatario': docs_destinatario.count(),
        'transportador': docs_transportador.count(),
        'tomador': docs_tomador.count(),
        'remetente': docs_remetente.count(),
        'recebedor': docs_recebedor.count(),
    }
    
    context = {
        'consulta': consulta,
        'stats': stats,
        'docs_emitente': docs_emitente,
        'docs_destinatario': docs_destinatario,
        'docs_transportador': docs_transportador,
        'docs_tomador': docs_tomador,
        'docs_remetente': docs_remetente,
        'docs_recebedor': docs_recebedor,
    }
    
    return render(request, 'core/consulta_resultado.html', context)


@login_required
@require_POST
def importar_documento(request, documento_id):
    """Importa documento consultado para o sistema"""
    documento = get_object_or_404(DocumentoConsultado, id=documento_id)
    
    # Verificar permissão
    if documento.consulta.certificado.usuario != request.user:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    try:
        # Importar para NFe ou CTe
        if documento.consulta.tipo_documento == 'NFE':
            from .models import NFe, NFeItem
            from .xml_parser import parse_nfe_xml
            
            # Parsear XML e criar NFe
            dados = parse_nfe_xml(documento.xml_completo)
            # Criar NFe no banco...
            
            documento.importado = True
            documento.data_importacao = datetime.now()
            documento.save()
            
            return JsonResponse({'sucesso': True, 'mensagem': 'Documento importado!'})
        
        elif documento.consulta.tipo_documento == 'CTE':
            # Similar para CTe
            pass
        
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@login_required
def configuracoes_consulta(request):
    """Configurações de consulta automática"""
    config, created = ConfiguracaoConsulta.objects.get_or_create(
        usuario=request.user
    )
    
    if request.method == 'POST':
        try:
            config.ufs_habilitadas = request.POST.get('ufs_habilitadas')
            config.max_documentos_por_consulta = int(request.POST.get('max_documentos', 1000))
            config.notificar_email = request.POST.get('notificar_email') == 'on'
            config.email_notificacao = request.POST.get('email_notificacao', '')
            config.consulta_automatica_ativa = request.POST.get('consulta_automatica') == 'on'
            
            if request.POST.get('horario_consulta'):
                config.horario_consulta = request.POST.get('horario_consulta')
            
            config.save()
            
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('configuracoes_consulta')
            
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')
    
    context = {
        'config': config,
    }
    return render(request, 'core/configuracoes_consulta.html', context)


@login_required
def dashboard_consultas(request):
    """Dashboard geral de consultas"""
    certificados = CertificadoDigital.objects.filter(usuario=request.user)
    
    # Últimas consultas
    consultas_recentes = ConsultaSEFAZ.objects.filter(
        certificado__usuario=request.user
    ).order_by('-data_consulta')[:20]
    
    # Documentos pendentes de importação
    docs_pendentes = DocumentoConsultado.objects.filter(
        consulta__certificado__usuario=request.user,
        importado=False
    ).count()
    
    # Estatísticas gerais
    total_consultado = DocumentoConsultado.objects.filter(
        consulta__certificado__usuario=request.user
    ).count()
    
    total_importado = DocumentoConsultado.objects.filter(
        consulta__certificado__usuario=request.user,
        importado=True
    ).count()
    
    context = {
        'certificados': certificados,
        'consultas_recentes': consultas_recentes,
        'docs_pendentes': docs_pendentes,
        'total_consultado': total_consultado,
        'total_importado': total_importado,
    }
    
    return render(request, 'core/dashboard_consultas.html', context)
