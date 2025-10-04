"""
Script de importação de XMLs para Google Cloud SQL
Processa todos os XMLs de NFe e CTe e insere no banco de dados
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import mysql.connector
from mysql.connector import Error
from xml_parser import XMLParser
import json
from datetime import datetime


class CloudSQLImporter:
    """Classe para importar XMLs para Google Cloud SQL"""

    def __init__(self, config: Dict):
        """
        Inicializa o importador

        Args:
            config: Dicionário com configurações de conexão
                {
                    'host': 'IP do Cloud SQL',
                    'user': 'usuário',
                    'password': 'senha',
                    'database': 'nome do banco',
                    'port': 3306
                }
        """
        self.config = config
        self.parser = XMLParser()
        self.connection = None
        self.stats = {
            'nfe_sucesso': 0,
            'nfe_erro': 0,
            'cte_sucesso': 0,
            'cte_erro': 0,
            'itens_inseridos': 0,
            'erros': []
        }

    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config.get('port', 3306),
                charset='utf8mb4',
                autocommit=False
            )

            if self.connection.is_connected():
                print(f"✓ Conectado ao Google Cloud SQL: {self.config['database']}")
                return True
        except Error as e:
            print(f"✗ Erro ao conectar ao banco: {e}")
            return False

    def disconnect(self):
        """Fecha a conexão com o banco"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Conexão fechada")

    def criar_tabelas(self):
        """Cria as tabelas no banco de dados"""
        try:
            cursor = self.connection.cursor()

            # Lê o arquivo de schema
            schema_path = Path(__file__).parent / 'database_schema.sql'
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Executa cada comando SQL
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)

            self.connection.commit()
            cursor.close()
            print("✓ Tabelas criadas/verificadas com sucesso")
            return True

        except Error as e:
            print(f"✗ Erro ao criar tabelas: {e}")
            return False

    def importar_nfe(self, xml_path: str) -> bool:
        """
        Importa uma NFe para o banco

        Args:
            xml_path: Caminho para o arquivo XML

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Parse do XML
            dados = self.parser.parse_nfe(xml_path)

            if 'error' in dados:
                self.log_erro('NFe', os.path.basename(xml_path), dados['error'])
                self.stats['nfe_erro'] += 1
                return False

            cursor = self.connection.cursor()

            # Verifica se já existe
            cursor.execute(
                "SELECT id FROM nfe WHERE chave_acesso = %s",
                (dados['chave_acesso'],)
            )

            if cursor.fetchone():
                print(f"  ⊳ NFe {dados['numero_nf']} já existe - pulando")
                cursor.close()
                return True

            # Insere NFe
            sql = """
                INSERT INTO nfe (
                    chave_acesso, numero_nf, serie, data_emissao,
                    emit_cnpj, emit_nome, emit_fantasia, emit_ie,
                    emit_endereco, emit_municipio, emit_uf, emit_cep,
                    dest_cnpj_cpf, dest_nome, dest_ie,
                    dest_endereco, dest_municipio, dest_uf, dest_cep,
                    valor_total, valor_produtos, valor_icms, valor_ipi,
                    valor_pis, valor_cofins, valor_tributos,
                    status_nfe, protocolo, motivo,
                    xml_content, arquivo_nome
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """

            valores = (
                dados.get('chave_acesso'),
                dados.get('numero_n'),
                dados.get('serie'),
                dados.get('data_emissao'),
                dados.get('cnpj'),
                dados.get('nome'),
                dados.get('fantasia'),
                dados.get('ie'),
                dados.get('endereco'),
                dados.get('municipio'),
                dados.get('u'),
                dados.get('cep'),
                dados.get('dest_cnpj_cp'),
                dados.get('dest_nome'),
                dados.get('dest_ie'),
                dados.get('dest_endereco'),
                dados.get('dest_municipio'),
                dados.get('dest_u'),
                dados.get('dest_cep'),
                dados.get('valor_total'),
                dados.get('valor_produtos'),
                dados.get('valor_icms'),
                dados.get('valor_ipi'),
                dados.get('valor_pis'),
                dados.get('valor_cofins'),
                dados.get('valor_tributos'),
                dados.get('status'),
                dados.get('protocolo'),
                dados.get('motivo'),
                dados.get('xml_content'),
                os.path.basename(xml_path)
            )

            cursor.execute(sql, valores)
            nfe_id = cursor.lastrowid

            # Insere itens
            if 'itens' in dados and dados['itens']:
                sql_item = """
                    INSERT INTO nfe_itens (
                        nfe_id, chave_acesso, numero_item,
                        codigo_produto, descricao, ncm, cfop, cest,
                        unidade, quantidade, valor_unitario, valor_total,
                        ean, valor_icms, valor_ipi, valor_pis, valor_cofins
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                """

                for item in dados['itens']:
                    valores_item = (
                        nfe_id,
                        dados['chave_acesso'],
                        item.get('numero_item'),
                        item.get('codigo_produto'),
                        item.get('descricao'),
                        item.get('ncm'),
                        item.get('cfop'),
                        item.get('cest'),
                        item.get('unidade'),
                        item.get('quantidade'),
                        item.get('valor_unitario'),
                        item.get('valor_total'),
                        item.get('ean'),
                        item.get('valor_icms'),
                        item.get('valor_ipi'),
                        item.get('valor_pis'),
                        item.get('valor_cofins')
                    )
                    cursor.execute(sql_item, valores_item)
                    self.stats['itens_inseridos'] += 1

            self.connection.commit()
            cursor.close()

            self.log_sucesso('NFe', os.path.basename(xml_path), dados['chave_acesso'])
            self.stats['nfe_sucesso'] += 1

            print(f"  ✓ NFe {dados['numero_nf']} importada ({len(dados.get('itens', []))} itens)")
            return True

        except Error as e:
            self.connection.rollback()
            self.log_erro('NFe', os.path.basename(xml_path), str(e))
            self.stats['nfe_erro'] += 1
            print(f"  ✗ Erro ao importar NFe: {e}")
            return False
        except Exception as e:
            self.connection.rollback()
            self.log_erro('NFe', os.path.basename(xml_path), str(e))
            self.stats['nfe_erro'] += 1
            print(f"  ✗ Erro inesperado: {e}")
            return False

    def importar_cte(self, xml_path: str) -> bool:
        """
        Importa um CTe para o banco

        Args:
            xml_path: Caminho para o arquivo XML

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Parse do XML
            dados = self.parser.parse_cte(xml_path)

            if 'error' in dados:
                self.log_erro('CTe', os.path.basename(xml_path), dados['error'])
                self.stats['cte_erro'] += 1
                return False

            cursor = self.connection.cursor()

            # Verifica se já existe
            cursor.execute(
                "SELECT id FROM cte WHERE chave_acesso = %s",
                (dados['chave_acesso'],)
            )

            if cursor.fetchone():
                print(f"  ⊳ CTe {dados['numero_ct']} já existe - pulando")
                cursor.close()
                return True

            # Insere CTe
            sql = """
                INSERT INTO cte (
                    chave_acesso, numero_ct, serie, data_emissao,
                    emit_cnpj, emit_nome, emit_fantasia, emit_ie,
                    emit_endereco, emit_municipio, emit_uf,
                    rem_cnpj, rem_nome, rem_ie, rem_municipio, rem_uf,
                    dest_cnpj, dest_nome, dest_ie, dest_municipio, dest_uf,
                    modal, tipo_servico, cfop, natureza_operacao,
                    municipio_inicio, uf_inicio, municipio_fim, uf_fim,
                    valor_total, valor_receber, valor_carga, valor_icms,
                    status_cte, protocolo, motivo,
                    xml_content, arquivo_nome
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )
            """

            valores = (
                dados.get('chave_acesso'),
                dados.get('numero_ct'),
                dados.get('serie'),
                dados.get('data_emissao'),
                dados.get('emit_cnpj'),
                dados.get('emit_nome'),
                dados.get('emit_fantasia'),
                dados.get('emit_ie'),
                dados.get('emit_endereco'),
                dados.get('emit_municipio'),
                dados.get('emit_u'),
                dados.get('rem_cnpj'),
                dados.get('rem_nome'),
                dados.get('rem_ie'),
                dados.get('rem_municipio'),
                dados.get('rem_u'),
                dados.get('dest_cnpj'),
                dados.get('dest_nome'),
                dados.get('dest_ie'),
                dados.get('dest_municipio'),
                dados.get('dest_u'),
                dados.get('modal'),
                dados.get('tipo_servico'),
                dados.get('cfop'),
                dados.get('natureza_operacao'),
                dados.get('municipio_inicio'),
                dados.get('uf_inicio'),
                dados.get('municipio_fim'),
                dados.get('uf_fim'),
                dados.get('valor_total'),
                dados.get('valor_receber'),
                dados.get('valor_carga'),
                dados.get('valor_icms'),
                dados.get('status'),
                dados.get('protocolo'),
                dados.get('motivo'),
                dados.get('xml_content'),
                os.path.basename(xml_path)
            )

            cursor.execute(sql, valores)
            self.connection.commit()
            cursor.close()

            self.log_sucesso('CTe', os.path.basename(xml_path), dados['chave_acesso'])
            self.stats['cte_sucesso'] += 1

            print(f"  ✓ CTe {dados['numero_ct']} importado")
            return True

        except Error as e:
            self.connection.rollback()
            self.log_erro('CTe', os.path.basename(xml_path), str(e))
            self.stats['cte_erro'] += 1
            print(f"  ✗ Erro ao importar CTe: {e}")
            return False
        except Exception as e:
            self.connection.rollback()
            self.log_erro('CTe', os.path.basename(xml_path), str(e))
            self.stats['cte_erro'] += 1
            print(f"  ✗ Erro inesperado: {e}")
            return False

    def log_sucesso(self, tipo: str, arquivo: str, chave: str):
        """Registra sucesso no log"""
        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO import_log (tipo_documento, arquivo_nome, status, chave_acesso)
                VALUES (%s, %s, 'sucesso', %s)
            """
            cursor.execute(sql, (tipo, arquivo, chave))
            cursor.close()
        except:
            pass  # Log é secundário, não deve interromper o processo

    def log_erro(self, tipo: str, arquivo: str, mensagem: str):
        """Registra erro no log"""
        self.stats['erros'].append({
            'tipo': tipo,
            'arquivo': arquivo,
            'mensagem': mensagem
        })

        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO import_log (tipo_documento, arquivo_nome, status, mensagem)
                VALUES (%s, %s, 'erro', %s)
            """
            cursor.execute(sql, (tipo, arquivo, mensagem[:500]))
            cursor.close()
        except:
            pass

    def processar_diretorio(self, diretorio: str, tipo: str):
        """
        Processa todos os XMLs de um diretório

        Args:
            diretorio: Caminho do diretório
            tipo: 'NFe' ou 'CTe'
        """
        path = Path(diretorio)

        if not path.exists():
            print(f"✗ Diretório não encontrado: {diretorio}")
            return

        # Lista todos os XMLs
        xml_files = list(path.glob('*.xml'))
        total = len(xml_files)

        print(f"\n{'='*60}")
        print(f"Processando {tipo}: {total} arquivos")
        print(f"{'='*60}")

        for idx, xml_file in enumerate(xml_files, 1):
            print(f"[{idx}/{total}] {xml_file.name}")

            if tipo == 'NFe':
                self.importar_nfe(str(xml_file))
            elif tipo == 'CTe':
                self.importar_cte(str(xml_file))

    def exibir_estatisticas(self):
        """Exibe estatísticas da importação"""
        print(f"\n{'='*60}")
        print("ESTATÍSTICAS DA IMPORTAÇÃO")
        print(f"{'='*60}")
        print("NFe:")
        print(f"  ✓ Sucesso: {self.stats['nfe_sucesso']}")
        print(f"  ✗ Erro: {self.stats['nfe_erro']}")
        print("\nCTe:")
        print(f"  ✓ Sucesso: {self.stats['cte_sucesso']}")
        print(f"  ✗ Erro: {self.stats['cte_erro']}")
        print(f"\nItens de NFe inseridos: {self.stats['itens_inseridos']}")
        print("\nTotal de documentos:")
        print(f"  ✓ Sucesso: {self.stats['nfe_sucesso'] + self.stats['cte_sucesso']}")
        print(f"  ✗ Erro: {self.stats['nfe_erro'] + self.stats['cte_erro']}")

        if self.stats['erros']:
            print(f"\n{'='*60}")
            print(f"ERROS ({len(self.stats['erros'])} primeiros):")
            print(f"{'='*60}")
            for erro in self.stats['erros'][:10]:
                print(f"  • {erro['tipo']}: {erro['arquivo']}")
                print(f"    {erro['mensagem'][:100]}")

        print(f"\n{'='*60}")


def main():
    """Função principal"""

    # Verifica se o arquivo de configuração existe
    config_path = Path(__file__).parent / 'config.json'

    if not config_path.exists():
        print("✗ Arquivo config.json não encontrado!")
        print("\nCrie um arquivo config.json com as seguintes informações:")
        print(json.dumps({
            "host": "IP_DO_CLOUD_SQL",
            "user": "usuario",
            "password": "senha",
            "database": "nome_do_banco",
            "port": 3306,
            "diretorios": {
                "nfe": "./NFe",
                "cte": "./CTe"
            }
        }, indent=2, ensure_ascii=False))
        return

    # Carrega configuração
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Inicializa importador
    importer = CloudSQLImporter(config)

    # Conecta ao banco
    if not importer.connect():
        return

    # Cria tabelas
    if not importer.criar_tabelas():
        importer.disconnect()
        return

    try:
        # Processa NFe
        nfe_dir = config.get('diretorios', {}).get('nfe', './NFe')
        importer.processar_diretorio(nfe_dir, 'NFe')

        # Processa CTe
        cte_dir = config.get('diretorios', {}).get('cte', './CTe')
        importer.processar_diretorio(cte_dir, 'CTe')

        # Exibe estatísticas
        importer.exibir_estatisticas()

    finally:
        importer.disconnect()


if __name__ == '__main__':
    main()
