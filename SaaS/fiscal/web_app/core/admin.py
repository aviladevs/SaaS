from django.contrib import admin
from .models import NFe, NFeItem, CTe, ImportLog


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
