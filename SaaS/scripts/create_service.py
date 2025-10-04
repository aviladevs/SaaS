#!/usr/bin/env python3
"""
Script para criar novos serviços usando templates padrão.

Uso: python scripts/create_service.py <nome-do-servico> <tipo>
"""

import os
import sys
import shutil
from pathlib import Path

def create_service(service_name: str, service_type: str = "django"):
    """
    Cria um novo serviço baseado no template padrão.

    Args:
        service_name: Nome do serviço em kebab-case (ex: user-management)
        service_type: Tipo do serviço (django, nextjs, reactnative)
    """

    if not service_name or not service_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Nome do serviço inválido. Use apenas letras, números, hífens e underscore.")
        sys.exit(1)

    # Converter para diferentes formatos
    service_name_kebab = service_name.lower()
    service_name_snake = service_name_kebab.replace('-', '_')
    service_name_pascal = ''.join(word.capitalize() for word in service_name_kebab.split('-'))
    service_name_camel = service_name_kebab[0].lower() + service_name_pascal[1:]

    # Diretório de destino
    services_dir = Path("apps")
    if not services_dir.exists():
        print("❌ Diretório 'apps' não encontrado. Execute este script da raiz do projeto.")
        sys.exit(1)

    new_service_dir = services_dir / service_name_kebab
    if new_service_dir.exists():
        print(f"❌ Serviço '{service_name_kebab}' já existe em apps/")
        sys.exit(1)

    # Template source
    template_dir = Path("templates/service-template")

    print(f"🚀 Criando novo serviço: {service_name_kebab}")
    print(f"📁 Tipo: {service_type}")
    print(f"📂 Destino: {new_service_dir}")

    try:
        # Copiar template
        shutil.copytree(template_dir, new_service_dir)
        print("✅ Template copiado com sucesso")

        # Personalizar arquivos
        customize_service_files(new_service_dir, {
            'service_name_kebab': service_name_kebab,
            'service_name_snake': service_name_snake,
            'service_name_pascal': service_name_pascal,
            'service_name_camel': service_name_camel,
        })

        print("✅ Arquivos personalizados")

        # Criar estrutura específica por tipo
        if service_type == "django":
            setup_django_service(new_service_dir, service_name_kebab, service_name_snake)
        elif service_type == "nextjs":
            setup_nextjs_service(new_service_dir, service_name_kebab)
        elif service_type == "reactnative":
            setup_reactnative_service(new_service_dir, service_name_kebab)

        print("✅ Estrutura específica criada")

        # Finalizar
        print_service_created_successfully(new_service_dir, service_name_kebab, service_type)

    except Exception as e:
        print(f"❌ Erro ao criar serviço: {e}")
        # Limpar em caso de erro
        if new_service_dir.exists():
            shutil.rmtree(new_service_dir)
        sys.exit(1)

def customize_service_files(service_dir: Path, replacements: dict):
    """Personaliza arquivos do template com os dados do serviço."""

    for root, dirs, files in os.walk(service_dir):
        for file in files:
            file_path = Path(root) / file

            # Pular arquivos binários e específicos
            if file.endswith(('.pyc', '.pyo', '.png', '.jpg', '.ico')):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Aplicar substituições
                for placeholder, value in replacements.items():
                    content = content.replace(f'{{{placeholder}}}', str(value))

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            except Exception as e:
                print(f"⚠️  Não foi possível personalizar {file_path}: {e}")

def setup_django_service(service_dir: Path, service_name_kebab: str, service_name_snake: str):
    """Configura estrutura específica para serviço Django."""

    # Renomear diretório Django
    django_src = service_dir / "src" / "service"
    django_dest = service_dir / "src" / service_name_snake

    if django_src.exists():
        os.rename(django_src, django_dest)

    # Atualizar imports no settings.py
    settings_file = django_dest / "settings.py"
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            content = f.read()

        # Corrigir nome do módulo WSGI
        content = content.replace(
            'WSGI_APPLICATION = \'service.wsgi.application\'',
            f'WSGI_APPLICATION = \'{service_name_snake}.wsgi.application\''
        )

        with open(settings_file, 'w') as f:
            f.write(content)

def setup_nextjs_service(service_dir: Path, service_name_kebab: str):
    """Configura estrutura específica para serviço Next.js."""

    # Renomear para estrutura Next.js
    nextjs_files = [
        'package.json',
        'next.config.js',
        'tailwind.config.js',
        'tsconfig.json'
    ]

    for file in nextjs_files:
        src = service_dir / file.replace('.json', '.json').replace('.js', '.js').replace('.ts', '.ts')
        if src.exists():
            # Já está correto
            pass

def setup_reactnative_service(service_dir: Path, service_name_kebab: str):
    """Configura estrutura específica para serviço React Native."""

    # Renomear para estrutura React Native
    rn_files = [
        'package.json',
        'App.tsx',
        'app.json'
    ]

    for file in rn_files:
        src = service_dir / file
        if src.exists():
            # Já está correto
            pass

def print_service_created_successfully(service_dir: Path, service_name: str, service_type: str):
    """Exibe mensagem de sucesso com instruções."""

    print(f"\n🎉 Serviço '{service_name}' criado com sucesso!")
    print("=" * 60)
    print(f"📂 Localização: {service_dir}")
    print(f"🔧 Tipo: {service_type}")
    print()
    print("📋 Próximos passos:")
    print(f"   1. cd {service_dir}")
    print("   2. cp .env.example .env"    print("   3. Edite .env com suas configurações"
    print("   4. docker-compose up -d"    print("   5. Acesse http://localhost:8000"
    print()
    print("🔗 Recursos disponíveis:")
    print(f"   • Documentação: {service_dir}/README.md")
    print("   • Estrutura padrão: templates/service-template/"
    print("   • Guias de desenvolvimento: docs/development/"
    print()
    print("🚀 Happy coding!"
def main():
    """Função principal."""

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Uso: python scripts/create_service.py <nome-do-servico> [tipo]")
        print("Tipos disponíveis: django (padrão), nextjs, reactnative")
        print()
        print("Exemplos:")
        print("  python scripts/create_service.py user-management")
        print("  python scripts/create_service.py product-catalog django")
        print("  python scripts/create_service.py admin-panel nextjs")
        sys.exit(1)

    service_name = sys.argv[1]
    service_type = sys.argv[2] if len(sys.argv) == 3 else "django"

    if service_type not in ["django", "nextjs", "reactnative"]:
        print(f"❌ Tipo de serviço inválido: {service_type}")
        print("Tipos disponíveis: django, nextjs, reactnative")
        sys.exit(1)

    create_service(service_name, service_type)

if __name__ == "__main__":
    main()
