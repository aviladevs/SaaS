from django.contrib import admin
from .models import NFe, NFeItem, CTe, ImportLog
from .webhooks import Webhook, WebhookLog
from .models_certificado import CertificadoDigital, ConsultaSEFAZ, DocumentoConsultado, ConfiguracaoConsulta


@admin.register(NFe)
class NFeAdmin(admin.ModelAdmin):
    list_display = ['numero_nf', 'emit_nome', 'dest_nome', 'valor_total', 'data_emissao']
    list_filter = ['data_emissao', 'emit_uf', 'status_nfe']
    search_fields = ['chave_acesso', 'numero_nf', 'emit_nome', 'dest_nome', 'emit_cnpj']
    date_hierarchy = 'data_emissao'
    readonly_fields = ['data_importacao']


@admin.register(NFeItem)
class NFeItemAdmin(admin.ModelAdmin):
    list_display = ['nfe', 'numero_item', 'descricao', 'quantidade', 'valor_total']
    list_filter = ['nfe__data_emissao']
    search_fields = ['descricao', 'codigo_produto']


@admin.register(CTe)
class CTeAdmin(admin.ModelAdmin):
    list_display = ['numero_ct', 'emit_nome', 'dest_nome', 'valor_total', 'data_emissao']
    list_filter = ['data_emissao', 'emit_uf', 'modal']
    search_fields = ['chave_acesso', 'numero_ct', 'emit_nome', 'dest_nome']
    date_hierarchy = 'data_emissao'
    readonly_fields = ['data_importacao']


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['arquivo_nome', 'tipo_documento', 'status', 'data_importacao', 'usuario']
    list_filter = ['tipo_documento', 'status', 'data_importacao']
    search_fields = ['arquivo_nome', 'chave_acesso', 'mensagem']
    readonly_fields = ['data_importacao']


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de webhooks"""
    list_display = ['nome', 'url', 'eventos', 'ativo', 'total_execucoes', 'total_erros', 'ultima_execucao']
    list_filter = ['ativo', 'data_criacao', 'usuario']
    search_fields = ['nome', 'url', 'eventos']
    readonly_fields = ['data_criacao', 'data_atualizacao', 'ultima_execucao', 'total_execucoes', 'total_erros']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'nome', 'url', 'eventos', 'ativo')
        }),
        ('Segurança', {
            'fields': ('secret_key', 'headers_customizados')
        }),
        ('Configurações', {
            'fields': ('timeout', 'retry_count')
        }),
        ('Estatísticas', {
            'fields': ('data_criacao', 'data_atualizacao', 'ultima_execucao', 'total_execucoes', 'total_erros')
        }),
    )


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """Admin para logs de webhooks"""
    list_display = ['webhook', 'evento', 'sucesso', 'status_code', 'data_execucao']
    list_filter = ['sucesso', 'evento', 'data_execucao']
    search_fields = ['webhook__nome', 'evento', 'payload', 'erro']
    readonly_fields = ['data_execucao']
    date_hierarchy = 'data_execucao'


@admin.register(CertificadoDigital)
class CertificadoDigitalAdmin(admin.ModelAdmin):
    """Admin para certificados digitais"""
    list_display = ['nome', 'cnpj', 'ativo', 'consulta_automatica', 'validade_fim', 'ultima_consulta']
    list_filter = ['ativo', 'consulta_automatica', 'data_cadastro']
    search_fields = ['nome', 'cnpj', 'emissor']
    readonly_fields = ['data_cadastro', 'data_atualizacao', 'ultima_consulta']
    fieldsets = (
        ('Identificação', {
            'fields': ('usuario', 'nome', 'cnpj')
        }),
        ('Certificado', {
            'fields': ('arquivo_pfx', 'senha_pfx', 'validade_inicio', 'validade_fim', 'emissor')
        }),
        ('Automação', {
            'fields': ('ativo', 'consulta_automatica', 'intervalo_consulta')
        }),
        ('Auditoria', {
            'fields': ('data_cadastro', 'data_atualizacao', 'ultima_consulta')
        }),
    )


@admin.register(ConsultaSEFAZ)
class ConsultaSEFAZAdmin(admin.ModelAdmin):
    """Admin para consultas SEFAZ"""
    list_display = ['certificado', 'tipo_documento', 'status', 'data_inicio', 'data_fim', 'total_encontrados']
    list_filter = ['tipo_documento', 'status', 'data_consulta']
    search_fields = ['certificado__nome', 'certificado__cnpj']
    readonly_fields = ['data_consulta', 'data_conclusao']
    date_hierarchy = 'data_consulta'


@admin.register(ConfiguracaoConsulta)
class ConfiguracaoConsultaAdmin(admin.ModelAdmin):
    """Admin para configurações de consulta"""
    list_display = ['usuario', 'consulta_automatica_ativa', 'horario_consulta', 'notificar_email']
    list_filter = ['consulta_automatica_ativa', 'notificar_email']
    search_fields = ['usuario__username', 'email_notificacao']
