#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Tenant Management Script
Gerencia tenants, domínios e configurações multi-tenant
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

from apps.users.models import User
from django.contrib.auth.models import Group


class TenantManager:
    """Gerenciador de tenants para SaaS"""

    def __init__(self):
        self.tenants_file = project_root / 'config' / 'tenants.json'
        self.tenants_file.parent.mkdir(exist_ok=True)

    def load_tenants(self):
        """Carrega configurações de tenants"""
        if self.tenants_file.exists():
            with open(self.tenants_file, 'r') as f:
                return json.load(f)
        return {}

    def save_tenants(self, tenants):
        """Salva configurações de tenants"""
        with open(self.tenants_file, 'w') as f:
            json.dump(tenants, f, indent=2)

    def create_tenant(self, name, domain, owner_email, plan='basic'):
        """Cria um novo tenant"""
        tenants = self.load_tenants()

        if name in tenants:
            raise ValueError(f"Tenant '{name}' já existe")

        # Criar usuário owner
        try:
            user = User.objects.create_user(
                username=f"{name}_owner",
                email=owner_email,
                first_name="Owner",
                last_name=name,
                company=name
            )
            user.is_verified = True
            user.save()

            # Criar grupo do tenant
            group, created = Group.objects.get_or_create(name=f"tenant_{name}")
            user.groups.add(group)

        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False

        # Configuração do tenant
        tenants[name] = {
            'domain': domain,
            'owner': owner_email,
            'plan': plan,
            'status': 'active',
            'created_at': str(os.times()),
            'settings': {
                'max_users': 100 if plan == 'basic' else 1000 if plan == 'pro' else -1,
                'storage_limit': 10,  # GB
                'features': self.get_plan_features(plan)
            }
        }

        self.save_tenants(tenants)
        print(f"Tenant '{name}' criado com sucesso!")
        print(f"Domínio: {domain}")
        print(f"Owner: {owner_email}")
        return True

    def get_plan_features(self, plan):
        """Retorna features do plano"""
        plans = {
            'basic': ['dashboard', 'basic_reports'],
            'pro': ['dashboard', 'advanced_reports', 'api_access', 'priority_support'],
            'enterprise': ['all_features', 'custom_integrations', 'dedicated_support', 'sla_99_9']
        }
        return plans.get(plan, plans['basic'])

    def list_tenants(self):
        """Lista todos os tenants"""
        tenants = self.load_tenants()

        if not tenants:
            print("Nenhum tenant encontrado")
            return

        print("\n=== TENANTS ATIVOS ===")
        print(f"{'Nome'"<20"} {'Domínio'"<30"} {'Plano'"<10"} {'Status'"<10"}")
        print("-" * 80)

        for name, config in tenants.items():
            print(f"{name"<20"} {config['domain']"<30"} {config['plan']"<10"} {config['status']"<10"}")

        print(f"\nTotal: {len(tenants)} tenants")

    def update_tenant(self, name, **kwargs):
        """Atualiza configurações de um tenant"""
        tenants = self.load_tenants()

        if name not in tenants:
            raise ValueError(f"Tenant '{name}' não encontrado")

        for key, value in kwargs.items():
            if key in tenants[name]:
                tenants[name][key] = value

        tenants[name]['updated_at'] = str(os.times())
        self.save_tenants(tenants)
        print(f"Tenant '{name}' atualizado com sucesso!")

    def delete_tenant(self, name):
        """Remove um tenant"""
        tenants = self.load_tenants()

        if name not in tenants:
            raise ValueError(f"Tenant '{name}' não encontrado")

        # Remover usuário e grupo
        try:
            user = User.objects.get(username=f"{name}_owner")
            user.delete()
            Group.objects.filter(name=f"tenant_{name}").delete()
        except User.DoesNotExist:
            pass

        del tenants[name]
        self.save_tenants(tenants)
        print(f"Tenant '{name}' removido com sucesso!")

    def backup_tenant(self, name):
        """Cria backup de um tenant"""
        tenants = self.load_tenants()

        if name not in tenants:
            raise ValueError(f"Tenant '{name}' não encontrado")

        # Criar diretório de backups
        backup_dir = project_root / 'backups' / 'tenants'
        backup_dir.mkdir(exist_ok=True)

        # Backup da configuração
        backup_file = backup_dir / f"{name}_backup.json"
        with open(backup_file, 'w') as f:
            json.dump({name: tenants[name]}, f, indent=2)

        print(f"Backup criado: {backup_file}")

    def restore_tenant(self, name, backup_file=None):
        """Restaura um tenant de backup"""
        if backup_file and os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
        else:
            # Buscar último backup
            backup_dir = project_root / 'backups' / 'tenants'
            backup_files = list(backup_dir.glob(f"{name}_backup*.json"))
            if not backup_files:
                raise ValueError(f"Nenhum backup encontrado para '{name}'")

            backup_file = max(backup_files, key=os.path.getctime)
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

        tenants = self.load_tenants()
        tenants.update(backup_data)
        self.save_tenants(tenants)

        print(f"Tenant '{name}' restaurado de: {backup_file}")


def main():
    parser = argparse.ArgumentParser(description='Gerenciador de Tenants Ávila DevOps SaaS')
    parser.add_argument('action', choices=[
        'create', 'update', 'delete', 'list', 'backup', 'restore'
    ], help='Ação a executar')

    parser.add_argument('--name', help='Nome do tenant')
    parser.add_argument('--domain', help='Domínio do tenant')
    parser.add_argument('--owner-email', help='Email do owner')
    parser.add_argument('--plan', choices=['basic', 'pro', 'enterprise'], default='basic')
    parser.add_argument('--backup-file', help='Arquivo de backup para restauração')

    args = parser.parse_args()

    manager = TenantManager()

    try:
        if args.action == 'create':
            if not all([args.name, args.domain, args.owner_email]):
                print("Erro: --name, --domain e --owner-email são obrigatórios para criar tenant")
                return
            manager.create_tenant(args.name, args.domain, args.owner_email, args.plan)

        elif args.action == 'update':
            if not args.name:
                print("Erro: --name é obrigatório para atualizar tenant")
                return
            kwargs = {}
            if args.domain:
                kwargs['domain'] = args.domain
            if args.plan:
                kwargs['plan'] = args.plan
            manager.update_tenant(args.name, **kwargs)

        elif args.action == 'delete':
            if not args.name:
                print("Erro: --name é obrigatório para deletar tenant")
                return
            manager.delete_tenant(args.name)

        elif args.action == 'list':
            manager.list_tenants()

        elif args.action == 'backup':
            if not args.name:
                print("Erro: --name é obrigatório para backup")
                return
            manager.backup_tenant(args.name)

        elif args.action == 'restore':
            if not args.name:
                print("Erro: --name é obrigatório para restauração")
                return
            manager.restore_tenant(args.name, args.backup_file)

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
