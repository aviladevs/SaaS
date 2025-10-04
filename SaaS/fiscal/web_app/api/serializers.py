"""
Serializers para API REST Mobile
"""
from rest_framework import serializers
from core.models import NFe, NFeItem, CTe, ImportLog


class NFeItemSerializer(serializers.ModelSerializer):
    """Serializer para itens de NFe"""

    class Meta:
        model = NFeItem
        fields = [
            'id', 'numero_item', 'codigo_produto', 'descricao',
            'ncm', 'cfop', 'unidade', 'quantidade', 'valor_unitario',
            'valor_total', 'valor_icms', 'valor_ipi'
        ]


class NFeListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de NFes (resumido)"""

    class Meta:
        model = NFe
        fields = [
            'id', 'chave_acesso', 'numero_n', 'serie', 'data_emissao',
            'emit_cnpj', 'emit_nome', 'dest_nome', 'valor_total',
            'status_nfe'
        ]


class NFeDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes completos de NFe"""

    itens = NFeItemSerializer(many=True, read_only=True)
    total_itens = serializers.SerializerMethodField()

    class Meta:
        model = NFe
        fields = '__all__'

    def get_total_itens(self, obj):
        return obj.itens.count()


class CTeListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de CTes (resumido)"""

    class Meta:
        model = CTe
        fields = [
            'id', 'chave_acesso', 'numero_ct', 'serie', 'data_emissao',
            'emit_cnpj', 'emit_nome', 'dest_nome', 'municipio_inicio',
            'municipio_fim', 'valor_total', 'status_cte'
        ]


class CTeDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes completos de CTe"""

    class Meta:
        model = CTe
        fields = '__all__'


class ImportLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de importação"""

    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = ImportLog
        fields = [
            'id', 'data_importacao', 'tipo_documento', 'arquivo_nome',
            'status', 'mensagem', 'chave_acesso', 'usuario_nome'
        ]


class DashboardSerializer(serializers.Serializer):
    """Serializer para dados do dashboard"""

    nfe_total = serializers.IntegerField()
    nfe_mes = serializers.IntegerField()
    nfe_valor_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    nfe_valor_mes = serializers.DecimalField(max_digits=15, decimal_places=2)

    cte_total = serializers.IntegerField()
    cte_mes = serializers.IntegerField()
    cte_valor_total = serializers.DecimalField(max_digits=15, decimal_places=2)
    cte_valor_mes = serializers.DecimalField(max_digits=15, decimal_places=2)

    ultimos_logs = ImportLogSerializer(many=True)


class StatisticsSerializer(serializers.Serializer):
    """Serializer para estatísticas e análises"""

    top_emitentes = serializers.ListField()
    top_produtos = serializers.ListField()
    top_rotas = serializers.ListField()
    vendas_por_mes = serializers.ListField()
