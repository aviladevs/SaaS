"""
Script de teste de conexão com Google Cloud SQL
Valida as credenciais e a conectividade antes de iniciar a importação
"""

import json
import mysql.connector
from mysql.connector import Error
from pathlib import Path


def test_connection():
    """Testa a conexão com o banco de dados"""

    print("="*60)
    print("TESTE DE CONEXÃO - GOOGLE CLOUD SQL")
    print("="*60)

    # Carrega configuração
    config_path = Path(__file__).parent / 'config.json'

    if not config_path.exists():
        print("\n✗ Arquivo config.json não encontrado!")
        print("\nPara criar o arquivo, copie config.json.example:")
        print("  copy config.json.example config.json")
        print("\nE edite com suas credenciais do Cloud SQL.")
        return False

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Valida configuração
    required_fields = ['host', 'user', 'password', 'database']
    missing = [f for f in required_fields if f not in config]

    if missing:
        print(f"\n✗ Campos obrigatórios faltando em config.json: {', '.join(missing)}")
        return False

    print("\n📋 Configuração:")
    print(f"   Host: {config['host']}")
    print(f"   User: {config['user']}")
    print(f"   Database: {config['database']}")
    print(f"   Port: {config.get('port', 3306)}")

    # Tenta conectar
    print("\n🔌 Tentando conectar...")

    try:
        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            port=config.get('port', 3306),
            connect_timeout=10
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("✓ Conexão estabelecida com sucesso!")
            print(f"✓ Versão do MySQL: {db_info}")

            # Testa query simples
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"✓ Banco de dados atual: {db_name}")

            # Verifica charset
            cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
            charset = cursor.fetchone()[1]
            print(f"✓ Charset do banco: {charset}")

            if charset != 'utf8mb4':
                print("  ⚠ Recomendação: Use utf8mb4 para suporte completo a caracteres especiais")

            # Lista tabelas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if tables:
                print(f"\n📊 Tabelas existentes ({len(tables)}):")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   • {table[0]}: {count} registros")
            else:
                print("\n📊 Nenhuma tabela encontrada (serão criadas na importação)")

            cursor.close()
            connection.close()

            print(f"\n{'='*60}")
            print("✓ TESTE CONCLUÍDO COM SUCESSO!")
            print("='*60}")
            print("\nVocê pode executar a importação:")
            print("  python import_to_cloudsql.py")
            print("="*60)

            return True

    except Error as e:
        print(f"\n✗ Erro ao conectar: {e}")
        print("\n💡 Possíveis soluções:")

        if "Can't connect" in str(e) or "timeout" in str(e):
            print("   1. Verifique se o IP do Cloud SQL está correto")
            print("   2. Confirme que seu IP está autorizado no Cloud SQL:")
            print("      - Acesse o Cloud Console")
            print("      - Vá para SQL > Sua Instância > Connections")
            print("      - Adicione seu IP em 'Authorized networks'")
            print("   3. Teste a conectividade: telnet {} {}".format(
                config['host'], config.get('port', 3306)))
            print("   4. Verifique se a instância Cloud SQL está ativa")

        elif "Access denied" in str(e):
            print("   1. Verifique o usuário e senha em config.json")
            print("   2. Confirme as permissões do usuário no banco:")
            print("      SHOW GRANTS FOR '{}'@'%';".format(config['user']))

        elif "Unknown database" in str(e):
            print("   1. Crie o banco de dados:")
            print("      CREATE DATABASE {} CHARACTER SET utf8mb4;".format(
                config['database']))

        print("")
        return False

    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        return False


if __name__ == '__main__':
    test_connection()
