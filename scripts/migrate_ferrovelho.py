#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Migração de Dados do Ferro Velho
Script para migrar dados da aplicação Streamlit original para o SaaS
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from apps.ferrovelho.models import SucataEntry, SucataMaterial, SucataItem
from apps.users.models import Tenant

def migrar_dados_ferrovelho():
    """Migrar dados da aplicação antiga para o SaaS"""

    print("🔄 Iniciando migração de dados do Ferro Velho...")
    print("=" * 60)

    # Verificar se arquivo CSV antigo existe
    csv_file = Path("sistema/parametros/entradas_sucata.csv")
    if not csv_file.exists():
        print("❌ Arquivo de dados antigo não encontrado!")
        print(f"   Procurando em: {csv_file.absolute()}")
        return False

    try:
        # Carregar dados antigos
        df_antigo = pd.read_csv(csv_file)
        print(f"✅ Dados antigos carregados: {len(df_antigo)} registros")

        # Obter ou criar tenant padrão
        tenant, created = Tenant.objects.get_or_create(
            name="Ferro Velho Roncato",
            defaults={
                'domain': 'ferrovelho.aviladevops.com.br',
                'contact_email': 'contato@ferrovelhoroncato.com.br',
                'is_active': True
            }
        )

        if created:
            print(f"✅ Tenant criado: {tenant.name}")

        # Migrar materiais (se ainda não existirem)
        materiais_existentes = set(
            SucataMaterial.objects.filter(tenant=tenant).values_list('nome', flat=True)
        )

        materiais_para_criar = []
        for col in df_antigo.columns:
            if col not in ['Cliente', 'Data', 'Hora', 'Observações'] and col not in materiais_existentes:
                materiais_para_criar.append({
                    'nome': col,
                    'categoria': 'Diversos',
                    'preco_base': 1.00,
                    'preco_atual': 1.00,
                    'unidade': 'kg'
                })

        if materiais_para_criar:
            for mat in materiais_para_criar:
                SucataMaterial.objects.create(tenant=tenant, **mat)
            print(f"✅ {len(materiais_para_criar)} materiais criados")

        # Migrar entradas
        entradas_migradas = 0
        entradas_ignoradas = 0

        for _, row in df_antigo.iterrows():
            cliente = str(row.get('Cliente', '')).strip()
            if not cliente or cliente.lower() == 'cliente':
                entradas_ignoradas += 1
                continue

            # Verificar se entrada já existe
            entrada_existente = SucataEntry.objects.filter(
                tenant=tenant,
                cliente=cliente,
                data=row['Data'],
                hora=row['Hora']
            ).first()

            if entrada_existente:
                entradas_ignoradas += 1
                continue

            # Criar entrada
            entrada = SucataEntry.objects.create(
                tenant=tenant,
                cliente=cliente,
                data=row['Data'],
                hora=row['Hora'],
                observacoes=str(row.get('Observações', '')),
                is_processed=False
            )

            # Criar itens
            materiais_cols = [col for col in df_antigo.columns
                            if col not in ['Cliente', 'Data', 'Hora', 'Observações']]

            itens_criados = 0
            for col in materiais_cols:
                quantidade = row.get(col, 0)
                if quantidade > 0:
                    try:
                        material = SucataMaterial.objects.get(
                            tenant=tenant,
                            nome=col,
                            is_active=True
                        )

                        SucataItem.objects.create(
                            entrada=entrada,
                            material=material,
                            quantidade=quantidade,
                            valor_unitario=material.preco_atual
                        )
                        itens_criados += 1

                    except SucataMaterial.DoesNotExist:
                        print(f"⚠️  Material '{col}' não encontrado para entrada de {cliente}")

            if itens_criados > 0:
                entradas_migradas += 1
                print(f"✅ Entrada migrada: {cliente} - {itens_criados} itens")
            else:
                # Remover entrada sem itens
                entrada.delete()
                entradas_ignoradas += 1

        print()
        print("📊 RESUMO DA MIGRAÇÃO:")
        print("=" * 30)
        print(f"📁 Registros no CSV antigo: {len(df_antigo)}")
        print(f"✅ Entradas migradas: {entradas_migradas}")
        print(f"⏭️  Entradas ignoradas: {entradas_ignoradas}")
        print(f"🏭 Tenant: {tenant.name}")
        print(f"📦 Materiais disponíveis: {SucataMaterial.objects.filter(tenant=tenant).count()}")

        # Backup do arquivo original
        backup_file = csv_file.with_suffix(f'.backup.{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df_antigo.to_csv(backup_file, index=False)
        print(f"💾 Backup criado: {backup_file}")

        return True

    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False

def verificar_integridade():
    """Verificar integridade dos dados migrados"""

    print("🔍 Verificando integridade dos dados...")

    try:
        # Verificar tenants
        tenants = Tenant.objects.all()
        print(f"🏭 Tenants encontrados: {tenants.count()}")

        for tenant in tenants:
            # Verificar materiais
            materiais = SucataMaterial.objects.filter(tenant=tenant)
            print(f"   📦 {tenant.name}: {materiais.count()} materiais")

            # Verificar entradas
            entradas = SucataEntry.objects.filter(tenant=tenant)
            print(f"   📋 {tenant.name}: {entradas.count()} entradas")

            # Verificar itens
            itens = SucataItem.objects.filter(entrada__tenant=tenant)
            print(f"   🧾 {tenant.name}: {itens.count()} itens")

            # Calcular totais
            total_kg = sum(item.quantidade for item in itens)
            valor_total = sum(item.valor_total for item in itens)

            print(f"   ⚖️  {tenant.name}: {total_kg:.1f}kg".1f" $ {valor_total:.2f}".2f"
        return True

    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🚀 Ávila DevOps SaaS - Migração Ferro Velho")
    print("=" * 60)
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--check-only':
        # Apenas verificar dados existentes
        verificar_integridade()
    else:
        # Executar migração
        sucesso = migrar_dados_ferrovelho()

        if sucesso:
            print()
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print()
            print("📋 PRÓXIMOS PASSOS:")
            print("1. Execute: python manage.py runserver")
            print("2. Acesse: http://localhost:8000/ferrovelho/")
            print("3. Teste a aplicação integrada")
            print("4. Execute migrações: python manage.py migrate")
            print()
            print("🔧 Para desenvolvimento:")
            print("   cd sistema/parametros")
            print("   streamlit run app.py")
            print()
            print("☁️  Para produção:")
            print("   A aplicação está integrada no SaaS!")
        else:
            print("❌ Migração falhou. Verifique os erros acima.")

if __name__ == '__main__':
    main()
