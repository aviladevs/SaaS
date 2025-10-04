"""
Django Signals para disparar webhooks automaticamente
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NFe, CTe, ImportLog
from .models_certificado import ConsultaSEFAZ
from .webhooks import disparar_webhook
from .notifications import notifier
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NFe)
def nfe_importada_signal(sender, instance, created, **kwargs):
    """Dispara webhook quando NFe é importada"""
    if created:
        try:
            dados = {
                'chave_acesso': instance.chave_acesso,
                'numero_nf': instance.numero_nf,
                'serie': instance.serie,
                'data_emissao': instance.data_emissao.isoformat() if instance.data_emissao else None,
                'emit_cnpj': instance.emit_cnpj,
                'emit_nome': instance.emit_nome,
                'dest_cnpj_cpf': instance.dest_cnpj_cpf,
                'dest_nome': instance.dest_nome,
                'valor_total': str(instance.valor_total) if instance.valor_total else '0',
                'valor_produtos': str(instance.valor_produtos) if instance.valor_produtos else '0',
                'status_nfe': instance.status_nfe,
            }
            
            # Dispara webhook para o usuário que importou
            if instance.usuario_importacao:
                disparar_webhook('nfe_importada', dados, usuario=instance.usuario_importacao)
                # Envia notificação por email
                notifier.notificar_nfe_importada(instance.usuario_importacao, instance)
            else:
                disparar_webhook('nfe_importada', dados)
                
            logger.info(f"Webhook disparado para NFe {instance.numero_nf}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar webhook para NFe {instance.id}: {str(e)}")


@receiver(post_save, sender=CTe)
def cte_importado_signal(sender, instance, created, **kwargs):
    """Dispara webhook quando CTe é importado"""
    if created:
        try:
            dados = {
                'chave_acesso': instance.chave_acesso,
                'numero_ct': instance.numero_ct,
                'serie': instance.serie,
                'data_emissao': instance.data_emissao.isoformat() if instance.data_emissao else None,
                'emit_cnpj': instance.emit_cnpj,
                'emit_nome': instance.emit_nome,
                'dest_cnpj': instance.dest_cnpj,
                'dest_nome': instance.dest_nome,
                'valor_total': str(instance.valor_total) if instance.valor_total else '0',
                'municipio_inicio': instance.municipio_inicio,
                'uf_inicio': instance.uf_inicio,
                'municipio_fim': instance.municipio_fim,
                'uf_fim': instance.uf_fim,
                'status_cte': instance.status_cte,
            }
            
            # Dispara webhook para o usuário que importou
            if instance.usuario_importacao:
                disparar_webhook('cte_importado', dados, usuario=instance.usuario_importacao)
                # Envia notificação por email
                notifier.notificar_cte_importado(instance.usuario_importacao, instance)
            else:
                disparar_webhook('cte_importado', dados)
                
            logger.info(f"Webhook disparado para CTe {instance.numero_ct}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar webhook para CTe {instance.id}: {str(e)}")


@receiver(post_save, sender=ImportLog)
def import_log_signal(sender, instance, created, **kwargs):
    """Dispara webhook quando há erro na importação"""
    if created and instance.status == 'erro':
        try:
            dados = {
                'tipo_documento': instance.tipo_documento,
                'arquivo_nome': instance.arquivo_nome,
                'chave_acesso': instance.chave_acesso,
                'mensagem': instance.mensagem,
                'data_importacao': instance.data_importacao.isoformat(),
            }
            
            # Dispara webhook de erro
            if instance.usuario:
                disparar_webhook('erro_importacao', dados, usuario=instance.usuario)
                # Envia notificação por email
                notifier.notificar_erro_importacao(instance.usuario, dados)
            else:
                disparar_webhook('erro_importacao', dados)
                
            logger.info(f"Webhook de erro disparado para {instance.arquivo_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar webhook de erro para log {instance.id}: {str(e)}")


@receiver(post_save, sender=ConsultaSEFAZ)
def consulta_concluida_signal(sender, instance, created, **kwargs):
    """Dispara webhook quando consulta SEFAZ é concluída"""
    if not created and instance.status == 'CONCLUIDA':
        try:
            dados = {
                'certificado_nome': instance.certificado.nome,
                'cnpj': instance.certificado.cnpj,
                'tipo_documento': instance.tipo_documento,
                'data_inicio': instance.data_inicio.isoformat(),
                'data_fim': instance.data_fim.isoformat(),
                'total_encontrados': instance.total_encontrados,
                'total_importados': instance.total_importados,
                'total_erros': instance.total_erros,
                'data_conclusao': instance.data_conclusao.isoformat() if instance.data_conclusao else None,
            }
            
            disparar_webhook('consulta_concluida', dados, usuario=instance.certificado.usuario)
            # Envia notificação por email
            notifier.notificar_consulta_concluida(instance.certificado.usuario, instance)
            logger.info(f"Webhook disparado para consulta SEFAZ concluída")
            
        except Exception as e:
            logger.error(f"Erro ao disparar webhook para consulta {instance.id}: {str(e)}")
