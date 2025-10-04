"""
Script para consultar e visualizar dados importados no Google Cloud SQL
Fornece relatórios e estatísticas dos XMLs importados
"""

import json
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from datetime import datetime
import sys


class ConsultaDados:
    """Classe para consultas e relatórios"""

    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config.get('port', 3306)
            )
            return True
        except Error as e:
            print(f"Erro ao conectar: {e}")
            return False

    def disconnect(self):
        """Fecha a conexão"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def executar_query(self, sql, params=None):
        """Executa uma query e retorna os resultados"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return columns, results
        except Error as e:
            print(f"Erro na query: {e}")
            return None, None

    def resumo_geral(self):
        """Exibe resumo geral dos dados"""
        print("\n" + "="*80)
        print("RESUMO GERAL")
        print("="*80)

        # Total de NFes
        sql = """
            SELECT
                COUNT(*) as total,
                SUM(valor_total) as valor_total,
                MIN(data_emissao) as primeira_data,
                MAX(data_emissao) as ultima_data
            FROM nfe
        """
        cols, results = self.executar_query(sql)
        if results and results[0][0]:
            print("\n📄 NOTAS FISCAIS (NFe):")
            print(f"   Total de notas: {results[0][0]:,}")
            print(f"   Valor total: R$ {results[0][1]:,.2f}" if results[0][1] else "   Valor total: R$ 0,00")
            if results[0][2]:
                print(f"   Período: {results[0][2]} até {results[0][3]}")

        # Total de itens
        sql = "SELECT COUNT(*) FROM nfe_itens"
        cols, results = self.executar_query(sql)
        if results:
            print(f"   Total de itens: {results[0][0]:,}")

        # Total de CTes
        sql = """
            SELECT
                COUNT(*) as total,
                SUM(valor_total) as valor_total,
                MIN(data_emissao) as primeira_data,
                MAX(data_emissao) as ultima_data
            FROM cte
        """
        cols, results = self.executar_query(sql)
        if results and results[0][0]:
            print("\n🚚 CONHECIMENTOS DE TRANSPORTE (CTe):")
            print(f"   Total de CTes: {results[0][0]:,}")
            print(f"   Valor total: R$ {results[0][1]:,.2f}" if results[0][1] else "   Valor total: R$ 0,00")
            if results[0][2]:
                print(f"   Período: {results[0][2]} até {results[0][3]}")

    def nfes_por_emitente(self, limite=10):
        """Lista NFes por emitente"""
        print("\n" + "="*80)
        print(f"TOP {limite} EMITENTES (NFe)")
        print("="*80)

        sql = """
            SELECT
                emit_cnpj,
                emit_nome,
                COUNT(*) as total_notas,
                SUM(valor_total) as valor_total
            FROM nfe
            WHERE emit_cnpj IS NOT NULL
            GROUP BY emit_cnpj, emit_nome
            ORDER BY total_notas DESC
            LIMIT %s
        """

        cols, results = self.executar_query(sql, (limite,))

        if results:
            print(f"\n{'CNPJ':<18} {'Nome':<40} {'Notas':>8} {'Valor Total':>15}")
            print("-" * 80)
            for row in results:
                cnpj = row[0] or "N/A"
                nome = (row[1] or "N/A")[:38]
                total = row[2]
                valor = row[3] or 0
                print(f"{cnpj:<18} {nome:<40} {total:>8} R$ {valor:>12,.2f}")

    def produtos_mais_vendidos(self, limite=10):
        """Lista produtos mais vendidos"""
        print("\n" + "="*80)
        print(f"TOP {limite} PRODUTOS MAIS VENDIDOS")
        print("="*80)

        sql = """
            SELECT
                codigo_produto,
                descricao,
                SUM(quantidade) as qtd_total,
                SUM(valor_total) as valor_total,
                COUNT(DISTINCT nfe_id) as num_notas
            FROM nfe_itens
            WHERE codigo_produto IS NOT NULL
            GROUP BY codigo_produto, descricao
            ORDER BY qtd_total DESC
            LIMIT %s
        """

        cols, results = self.executar_query(sql, (limite,))

        if results:
            print(f"\n{'Código':<15} {'Descrição':<40} {'Qtd':>10} {'Valor':>15}")
            print("-" * 80)
            for row in results:
                codigo = (row[0] or "N/A")[:13]
                descricao = (row[1] or "N/A")[:38]
                qtd = row[2] or 0
                valor = row[3] or 0
                print(f"{codigo:<15} {descricao:<40} {qtd:>10,.2f} R$ {valor:>12,.2f}")

    def ctes_por_rota(self, limite=10):
        """Lista CTes por rota"""
        print("\n" + "="*80)
        print(f"TOP {limite} ROTAS MAIS UTILIZADAS (CTe)")
        print("="*80)

        sql = """
            SELECT
                municipio_inicio,
                uf_inicio,
                municipio_fim,
                uf_fim,
                COUNT(*) as total_ctes,
                SUM(valor_total) as valor_total
            FROM cte
            WHERE municipio_inicio IS NOT NULL AND municipio_fim IS NOT NULL
            GROUP BY municipio_inicio, uf_inicio, municipio_fim, uf_fim
            ORDER BY total_ctes DESC
            LIMIT %s
        """

        cols, results = self.executar_query(sql, (limite,))

        if results:
            print(f"\n{'Origem':<30} {'Destino':<30} {'CTes':>8} {'Valor Total':>15}")
            print("-" * 80)
            for row in results:
                origem = f"{row[0]}/{row[1]}"[:28]
                destino = f"{row[2]}/{row[3]}"[:28]
                total = row[4]
                valor = row[5] or 0
                print(f"{origem:<30} {destino:<30} {total:>8} R$ {valor:>12,.2f}")

    def log_importacao(self, limite=20):
        """Exibe log de importação"""
        print("\n" + "="*80)
        print(f"LOG DE IMPORTAÇÃO (Últimos {limite})")
        print("="*80)

        sql = """
            SELECT
                data_importacao,
                tipo_documento,
                arquivo_nome,
                status,
                mensagem
            FROM import_log
            ORDER BY data_importacao DESC
            LIMIT %s
        """

        cols, results = self.executar_query(sql, (limite,))

        if results:
            for row in results:
                data = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else 'N/A'
                tipo = row[1]
                arquivo = row[2][:30]
                status = row[3]
                emoji = "✓" if status == 'sucesso' else "✗"

                print(f"\n{emoji} [{data}] {tipo}: {arquivo}")
                if status == 'erro' and row[4]:
                    print(f"   Erro: {row[4][:100]}")

        # Resumo do log
        sql = """
            SELECT
                tipo_documento,
                status,
                COUNT(*) as total
            FROM import_log
            GROUP BY tipo_documento, status
        """

        cols, results = self.executar_query(sql)

        if results:
            print("\n" + "-" * 80)
            print("RESUMO DO LOG:")
            for row in results:
                print(f"   {row[0]} - {row[1]}: {row[2]:,}")

    def vendas_por_periodo(self):
        """Vendas agrupadas por mês"""
        print("\n" + "="*80)
        print("VENDAS POR MÊS (NFe)")
        print("="*80)

        sql = """
            SELECT
                DATE_FORMAT(data_emissao, '%Y-%m') as mes,
                COUNT(*) as total_notas,
                SUM(valor_total) as valor_total
            FROM nfe
            WHERE data_emissao IS NOT NULL
            GROUP BY DATE_FORMAT(data_emissao, '%Y-%m')
            ORDER BY mes DESC
            LIMIT 12
        """

        cols, results = self.executar_query(sql)

        if results:
            print(f"\n{'Mês':<10} {'Notas':>10} {'Valor Total':>15}")
            print("-" * 80)
            for row in results:
                mes = row[0]
                total = row[1]
                valor = row[2] or 0
                print(f"{mes:<10} {total:>10,} R$ {valor:>12,.2f}")

    def menu(self):
        """Menu interativo"""
        while True:
            print("\n" + "="*80)
            print("CONSULTA DE DADOS - GOOGLE CLOUD SQL")
            print("="*80)
            print("\nEscolha uma opção:")
            print("  1. Resumo Geral")
            print("  2. NFes por Emitente")
            print("  3. Produtos Mais Vendidos")
            print("  4. CTes por Rota")
            print("  5. Vendas por Período")
            print("  6. Log de Importação")
            print("  7. Todos os Relatórios")
            print("  0. Sair")

            opcao = input("\nOpção: ").strip()

            if opcao == '0':
                print("\nEncerrando...")
                break
            elif opcao == '1':
                self.resumo_geral()
            elif opcao == '2':
                self.nfes_por_emitente()
            elif opcao == '3':
                self.produtos_mais_vendidos()
            elif opcao == '4':
                self.ctes_por_rota()
            elif opcao == '5':
                self.vendas_por_periodo()
            elif opcao == '6':
                self.log_importacao()
            elif opcao == '7':
                self.resumo_geral()
                self.nfes_por_emitente()
                self.produtos_mais_vendidos()
                self.ctes_por_rota()
                self.vendas_por_periodo()
                self.log_importacao()
            else:
                print("\nOpção inválida!")

            input("\nPressione ENTER para continuar...")


def main():
    """Função principal"""

    # Carrega configuração
    config_path = Path(__file__).parent / 'config.json'

    if not config_path.exists():
        print("✗ Arquivo config.json não encontrado!")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Conecta e executa
    consulta = ConsultaDados(config)

    if not consulta.connect():
        return

    try:
        # Se tiver argumentos, executa direto
        if len(sys.argv) > 1:
            if sys.argv[1] == '--all':
                consulta.resumo_geral()
                consulta.nfes_por_emitente()
                consulta.produtos_mais_vendidos()
                consulta.ctes_por_rota()
                consulta.vendas_por_periodo()
                consulta.log_importacao()
            elif sys.argv[1] == '--resumo':
                consulta.resumo_geral()
        else:
            # Menu interativo
            consulta.menu()
    finally:
        consulta.disconnect()


if __name__ == '__main__':
    main()
