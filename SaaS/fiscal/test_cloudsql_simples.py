"""
Teste SIMPLES de conexão com Google Cloud SQL
Usa apenas mysql-connector-python (já instalado)
"""

import json
from pathlib import Path
import sys

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ mysql-connector-python não instalado!")
    print("\nInstale com: pip install mysql-connector-python")
    sys.exit(1)


def testar_conexao():
    """Testa conexão com Cloud SQL"""

    print("="*60)
    print("  TESTE DE CONEXÃO - GOOGLE CLOUD SQL")
    print("="*60)

    # Carrega configuração
    config_path = Path(__file__).parent / 'config.json'

    if not config_path.exists():
        print("\n❌ Arquivo config.json não encontrado!")
        print("\nCrie o arquivo config.json com:")
        print("""
{
  "host": "IP_DO_CLOUD_SQL",
  "user": "seu_usuario",
  "password": "sua_senha",
  "database": "xml_fiscais",
  "port": 3306
}
        """)
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    print("\n📋 Configuração:")
    print(f"   Host: {config['host']}")
    print(f"   User: {config['user']}")
    print(f"   Database: {config['database']}")
    print(f"   Port: {config.get('port', 3306)}")

    # Tenta conectar
    print("\n🔌 Conectando...")

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
            print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")

            cursor = connection.cursor()

            # Versão MySQL
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"\n✅ Versão MySQL: {version}")

            # Banco atual
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()[0]
            print(f"✅ Banco atual: {db}")

            # Charset
            cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
            charset = cursor.fetchone()[1]
            print(f"✅ Charset: {charset}")

            # Lista tabelas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            if tables:
                print(f"\n📊 Tabelas existentes ({len(tables)}):")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   • {table[0]}: {count:,} registros")
            else:
                print("\n📊 Nenhuma tabela encontrada")
                print("   Execute: python import_to_cloudsql.py para criar")

            cursor.close()
            connection.close()

            print(f"\n{'='*60}")
            print("✅ TESTE CONCLUÍDO COM SUCESSO!")
            print(f"{'='*60}")
            print("\n✅ Você pode usar o Cloud SQL!")
            print("\nPróximos passos:")
            print("  1. Para importar XMLs:")
            print("     python import_to_cloudsql.py")
            print("\n  2. Para usar interface web:")
            print("     cd web_app")
            print("     Configure settings.py com Cloud SQL")
            print("     python manage.py migrate")
            print("     python manage.py runserver")

            return True

    except Error as e:
        print(f"\n❌ ERRO DE CONEXÃO: {e}")
        print("\n💡 Soluções:")

        error_str = str(e)

        if "Can't connect" in error_str or "timeout" in error_str:
            print("\n   🔧 Problema de Rede/Firewall:")
            print("   1. Verifique se o IP do Cloud SQL está correto")
            print("   2. No Google Cloud Console:")
            print("      • Vá em SQL > Sua Instância > Connections")
            print("      • Em 'Authorized networks' adicione seu IP")
            print("      • Ou adicione 0.0.0.0/0 para testes (não seguro!)")
            print("   3. Teste conectividade:")
            print(f"      telnet {config['host']} {config.get('port', 3306)}")
            print("   4. Verifique se a instância está ATIVA")

        elif "Access denied" in error_str:
            print("\n   🔧 Problema de Autenticação:")
            print("   1. Verifique usuário e senha em config.json")
            print("   2. No Cloud SQL, crie/verifique o usuário:")
            print(f"      CREATE USER '{config['user']}'@'%' IDENTIFIED BY 'sua_senha';")
            print(f"      GRANT ALL ON {config['database']}.* TO '{config['user']}'@'%';")
            print("      FLUSH PRIVILEGES;")

        elif "Unknown database" in error_str:
            print("\n   🔧 Banco de Dados não existe:")
            print("   1. Conecte ao Cloud SQL e crie o banco:")
            print(f"      CREATE DATABASE {config['database']} CHARACTER SET utf8mb4;")

        else:
            print("\n   🔧 Erro desconhecido. Verifique:")
            print("   1. Configurações do Cloud SQL")
            print("   2. Regras de firewall")
            print("   3. Credenciais de acesso")

        return False

    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        return False


def criar_config_exemplo():
    """Cria arquivo de configuração exemplo"""
    config_exemplo = {
        "host": "34.xxx.xxx.xxx",
        "user": "xml_user",
        "password": "senha_segura",
        "database": "xml_fiscais",
        "port": 3306,
        "diretorios": {
            "nfe": "./NFe",
            "cte": "./CTe"
        }
    }

    config_path = Path(__file__).parent / 'config.json.example'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_exemplo, f, indent=2, ensure_ascii=False)

    print("✅ Arquivo config.json.example criado!")


if __name__ == '__main__':
    print("\n")
    resultado = testar_conexao()
    print("\n")

    if not resultado:
        print("💡 Dica: Copie config.json.example e edite com suas credenciais")
        print("   copy config.json.example config.json")

    input("\nPressione ENTER para sair...")
