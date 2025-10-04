"""
Sistema de Notificações por Email e Webhook
Envia alertas para usuários sobre eventos importantes
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Serviço centralizado de notificações
    
    Uso:
        notifier = NotificationService()
        notifier.notificar_nfe_importada(user, nfe)
        notifier.notificar_erro_importacao(user, erro_info)
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@fiscal.com')
    
    def notificar_nfe_importada(self, usuario, nfe):
        """
        Notifica usuário sobre importação de NFe
        
        Args:
            usuario: Objeto User
            nfe: Objeto NFe
        """
        if not usuario.email:
            return
        
        assunto = f"✅ NFe {nfe.numero_nf} importada com sucesso"
        
        contexto = {
            'usuario': usuario,
            'nfe': nfe,
            'data': timezone.now()
        }
        
        # Texto simples
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

Uma nova NFe foi importada com sucesso:

Número: {nfe.numero_nf}
Série: {nfe.serie}
Emitente: {nfe.emit_nome}
Destinatário: {nfe.dest_nome}
Valor Total: R$ {nfe.valor_total}
Data Emissão: {nfe.data_emissao.strftime('%d/%m/%Y') if nfe.data_emissao else 'N/A'}

Chave de Acesso: {nfe.chave_acesso}

---
Esta é uma notificação automática do Sistema Fiscal.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Email de NFe importada enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email para {usuario.email}: {str(e)}")
    
    def notificar_cte_importado(self, usuario, cte):
        """Notifica usuário sobre importação de CTe"""
        if not usuario.email:
            return
        
        assunto = f"✅ CTe {cte.numero_ct} importado com sucesso"
        
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

Um novo CTe foi importado com sucesso:

Número: {cte.numero_ct}
Série: {cte.serie}
Emitente: {cte.emit_nome}
Destinatário: {cte.dest_nome}
Valor Total: R$ {cte.valor_total}
Origem: {cte.municipio_inicio}/{cte.uf_inicio}
Destino: {cte.municipio_fim}/{cte.uf_fim}

Chave de Acesso: {cte.chave_acesso}

---
Esta é uma notificação automática do Sistema Fiscal.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Email de CTe importado enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email para {usuario.email}: {str(e)}")
    
    def notificar_erro_importacao(self, usuario, erro_info):
        """Notifica usuário sobre erro na importação"""
        if not usuario.email:
            return
        
        assunto = "❌ Erro na importação de documento fiscal"
        
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

Ocorreu um erro ao importar um documento fiscal:

Tipo: {erro_info.get('tipo_documento', 'N/A')}
Arquivo: {erro_info.get('arquivo_nome', 'N/A')}
Erro: {erro_info.get('mensagem', 'Erro desconhecido')}

Por favor, verifique o arquivo e tente novamente.

---
Esta é uma notificação automática do Sistema Fiscal.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Email de erro enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email para {usuario.email}: {str(e)}")
    
    def notificar_consulta_concluida(self, usuario, consulta):
        """Notifica usuário sobre conclusão de consulta SEFAZ"""
        if not usuario.email:
            return
        
        assunto = f"📊 Consulta SEFAZ concluída - {consulta.total_encontrados} documentos"
        
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

A consulta automática SEFAZ foi concluída:

Certificado: {consulta.certificado.nome}
CNPJ: {consulta.certificado.cnpj}
Tipo: {consulta.tipo_documento}
Período: {consulta.data_inicio.strftime('%d/%m/%Y')} a {consulta.data_fim.strftime('%d/%m/%Y')}

Resultados:
- Documentos encontrados: {consulta.total_encontrados}
- Documentos importados: {consulta.total_importados}
- Erros: {consulta.total_erros}

---
Esta é uma notificação automática do Sistema Fiscal.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Email de consulta concluída enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email para {usuario.email}: {str(e)}")
    
    def enviar_resumo_diario(self, usuario, estatisticas):
        """Envia resumo diário de atividades"""
        if not usuario.email:
            return
        
        ontem = timezone.now() - timedelta(days=1)
        assunto = f"📈 Resumo Diário - {ontem.strftime('%d/%m/%Y')}"
        
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

Segue o resumo das suas atividades fiscais de ontem ({ontem.strftime('%d/%m/%Y')}):

📄 NOTAS FISCAIS (NFe):
- Total importadas: {estatisticas.get('nfes_importadas', 0)}
- Valor total: R$ {estatisticas.get('valor_total_nfe', 0):,.2f}
- Principais emitentes: {', '.join(estatisticas.get('top_emitentes', [])[:3])}

🚚 CONHECIMENTOS DE TRANSPORTE (CTe):
- Total importados: {estatisticas.get('ctes_importados', 0)}
- Valor total: R$ {estatisticas.get('valor_total_cte', 0):,.2f}
- Principais rotas: {', '.join(estatisticas.get('top_rotas', [])[:3])}

📊 CONSULTAS SEFAZ:
- Consultas realizadas: {estatisticas.get('consultas_realizadas', 0)}
- Documentos encontrados: {estatisticas.get('documentos_encontrados', 0)}

❌ ERROS:
- Erros de importação: {estatisticas.get('erros_importacao', 0)}

---
Esta é uma notificação automática do Sistema Fiscal.
Acesse o sistema para ver mais detalhes.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Resumo diário enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar resumo para {usuario.email}: {str(e)}")
    
    def notificar_certificado_vencendo(self, usuario, certificado, dias_restantes):
        """Notifica sobre certificado próximo do vencimento"""
        if not usuario.email:
            return
        
        assunto = f"⚠️ Certificado Digital vencendo em {dias_restantes} dias"
        
        mensagem_texto = f"""
Olá {usuario.first_name or usuario.username},

ATENÇÃO: Seu certificado digital está próximo do vencimento!

Certificado: {certificado.nome}
CNPJ: {certificado.cnpj}
Validade: até {certificado.validade_fim.strftime('%d/%m/%Y')}
Dias restantes: {dias_restantes}

Por favor, renove seu certificado o quanto antes para evitar interrupções
nas consultas automáticas SEFAZ.

---
Esta é uma notificação automática do Sistema Fiscal.
        """
        
        try:
            send_mail(
                assunto,
                mensagem_texto,
                self.from_email,
                [usuario.email],
                fail_silently=False,
            )
            logger.info(f"Alerta de certificado vencendo enviado para {usuario.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar alerta para {usuario.email}: {str(e)}")


# Instância global do serviço
notifier = NotificationService()
