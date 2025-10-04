"""
Sistema de Tarefas Agendadas (Background Tasks)
Executa tarefas automáticas como consultas SEFAZ, sincronizações, etc.
"""
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models_certificado import CertificadoDigital, ConsultaSEFAZ, ConfiguracaoConsulta
from core.sefaz_service import SEFAZService
from core.webhooks import disparar_webhook

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Executa tarefas agendadas: consultas automáticas SEFAZ, notificações, etc.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            help='Executar tarefa específica: consultas_sefaz, limpeza_logs, enviar_relatorios',
        )

    def handle(self, *args, **options):
        task = options.get('task')
        
        if task == 'consultas_sefaz':
            self.executar_consultas_sefaz()
        elif task == 'limpeza_logs':
            self.limpar_logs_antigos()
        elif task == 'enviar_relatorios':
            self.enviar_relatorios_diarios()
        else:
            # Executa todas as tarefas
            self.stdout.write("🔄 Iniciando execução de tarefas agendadas...")
            self.executar_consultas_sefaz()
            self.limpar_logs_antigos()
            self.enviar_relatorios_diarios()
            self.stdout.write(self.style.SUCCESS("✓ Todas as tarefas concluídas"))

    def executar_consultas_sefaz(self):
        """Executa consultas automáticas SEFAZ configuradas"""
        self.stdout.write("📊 Verificando consultas automáticas SEFAZ...")
        
        # Busca certificados com consulta automática ativa
        certificados = CertificadoDigital.objects.filter(
            ativo=True,
            consulta_automatica=True
        )
        
        agora = timezone.now()
        total_executadas = 0
        
        for cert in certificados:
            try:
                # Verifica se já passou o intervalo desde a última consulta
                if cert.ultima_consulta:
                    proxima_consulta = cert.ultima_consulta + timedelta(minutes=cert.intervalo_consulta)
                    if agora < proxima_consulta:
                        continue
                
                # Verifica se certificado está válido
                if not cert.esta_valido():
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Certificado {cert.nome} vencido")
                    )
                    continue
                
                # Executa consulta automática
                self.stdout.write(f"🔍 Consultando SEFAZ para {cert.nome}...")
                
                # Define período (últimos 7 dias)
                data_fim = agora.date()
                data_inicio = data_fim - timedelta(days=7)
                
                # Cria registro de consulta
                consulta = ConsultaSEFAZ.objects.create(
                    certificado=cert,
                    tipo_documento='NFE',
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    status='PROCESSANDO'
                )
                
                try:
                    # Executa consulta
                    sefaz_service = SEFAZService()
                    resultados = sefaz_service.consultar_documentos(
                        certificado=cert,
                        tipo_documento='NFE',
                        data_inicio=data_inicio,
                        data_fim=data_fim
                    )
                    
                    # Atualiza consulta
                    consulta.status = 'CONCLUIDA'
                    consulta.total_encontrados = len(resultados)
                    consulta.data_conclusao = timezone.now()
                    consulta.save()
                    
                    # Atualiza certificado
                    cert.ultima_consulta = timezone.now()
                    cert.save(update_fields=['ultima_consulta'])
                    
                    # Dispara webhook
                    disparar_webhook('consulta_concluida', {
                        'certificado': cert.nome,
                        'cnpj': cert.cnpj,
                        'total_encontrados': len(resultados),
                        'data_inicio': data_inicio.isoformat(),
                        'data_fim': data_fim.isoformat()
                    }, usuario=cert.usuario)
                    
                    total_executadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Consulta concluída: {len(resultados)} documentos encontrados")
                    )
                    
                except Exception as e:
                    logger.error(f"Erro ao consultar SEFAZ para {cert.nome}: {str(e)}")
                    consulta.status = 'ERRO'
                    consulta.mensagem_erro = str(e)
                    consulta.data_conclusao = timezone.now()
                    consulta.save()
                    
                    self.stdout.write(
                        self.style.ERROR(f"✗ Erro na consulta: {str(e)}")
                    )
                    
            except Exception as e:
                logger.error(f"Erro ao processar certificado {cert.id}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"✗ Erro ao processar certificado: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"✓ {total_executadas} consultas executadas")
        )

    def limpar_logs_antigos(self):
        """Remove logs antigos para otimizar banco de dados"""
        self.stdout.write("🧹 Limpando logs antigos...")
        
        try:
            from core.webhooks import WebhookLog
            from core.models import ImportLog
            
            # Remove logs de webhook com mais de 30 dias
            data_limite = timezone.now() - timedelta(days=30)
            webhook_logs_removidos = WebhookLog.objects.filter(
                data_execucao__lt=data_limite
            ).delete()[0]
            
            # Remove logs de importação com mais de 90 dias
            data_limite_import = timezone.now() - timedelta(days=90)
            import_logs_removidos = ImportLog.objects.filter(
                data_importacao__lt=data_limite_import,
                status='sucesso'  # Mantém logs de erro
            ).delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Removidos {webhook_logs_removidos} logs de webhook e "
                    f"{import_logs_removidos} logs de importação"
                )
            )
            
        except Exception as e:
            logger.error(f"Erro ao limpar logs: {str(e)}")
            self.stdout.write(self.style.ERROR(f"✗ Erro ao limpar logs: {str(e)}"))

    def enviar_relatorios_diarios(self):
        """Envia relatórios diários por email para usuários configurados"""
        self.stdout.write("📧 Enviando relatórios diários...")
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            from core.models import NFe, CTe
            
            # Busca configurações com notificação ativa
            configs = ConfiguracaoConsulta.objects.filter(
                notificar_email=True,
                email_notificacao__isnull=False
            ).exclude(email_notificacao='')
            
            ontem = timezone.now() - timedelta(days=1)
            total_enviados = 0
            
            for config in configs:
                try:
                    # Estatísticas do dia anterior
                    nfes_dia = NFe.objects.filter(
                        usuario_importacao=config.usuario,
                        data_importacao__gte=ontem
                    ).count()
                    
                    ctes_dia = CTe.objects.filter(
                        usuario_importacao=config.usuario,
                        data_importacao__gte=ontem
                    ).count()
                    
                    if nfes_dia == 0 and ctes_dia == 0:
                        continue
                    
                    # Envia email
                    assunto = f"Relatório Diário - {ontem.strftime('%d/%m/%Y')}"
                    mensagem = f"""
Olá {config.usuario.first_name or config.usuario.username},

Segue o relatório de documentos importados ontem ({ontem.strftime('%d/%m/%Y')}):

📄 NFe importadas: {nfes_dia}
🚚 CTe importados: {ctes_dia}

Total: {nfes_dia + ctes_dia} documentos

---
Este é um email automático do Sistema Fiscal.
                    """
                    
                    send_mail(
                        assunto,
                        mensagem,
                        settings.DEFAULT_FROM_EMAIL,
                        [config.email_notificacao],
                        fail_silently=False,
                    )
                    
                    total_enviados += 1
                    self.stdout.write(f"✓ Relatório enviado para {config.email_notificacao}")
                    
                except Exception as e:
                    logger.error(f"Erro ao enviar relatório para {config.usuario.username}: {str(e)}")
                    self.stdout.write(
                        self.style.ERROR(f"✗ Erro ao enviar para {config.email_notificacao}: {str(e)}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f"✓ {total_enviados} relatórios enviados")
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatórios: {str(e)}")
            self.stdout.write(self.style.ERROR(f"✗ Erro ao enviar relatórios: {str(e)}"))
