#!/usr/bin/env python3
"""
Ávila DevOps SaaS - Controle de Sucata (Ferro Velho)
Aplicação Streamlit integrada ao sistema multi-tenant
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importar Django
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

# Importar modelos do SaaS
from apps.ferrovelho.models import SucataEntry, SucataMaterial, SucataItem

# --- Configurações ---
LOGO_FILE = "logo.png"
COMPANY_INFO_FILE = "company_info.json"

def get_tenant_from_session():
    """Obter tenant da sessão ou usar padrão"""
    # Em produção, isso seria obtido da sessão do usuário
    # Por enquanto, usar tenant padrão ou primeiro disponível
    try:
        from apps.users.models import Tenant
        return Tenant.objects.first()  # Tenant padrão para desenvolvimento
    except:
        return None

def get_company_info(tenant=None):
    """Obter informações da empresa/tenant"""
    if tenant:
        return {
            "nome": tenant.name,
            "endereco": tenant.address or "Endereço não informado",
            "email": tenant.contact_email or "contato@empresa.com.br",
            "site": tenant.website or "https://empresa.com.br",
            "cnpj": getattr(tenant, 'cnpj', '') or "00.000.000/0000-00",
        }

    # Dados padrão para desenvolvimento
    return {
        "nome": "Ferro Velho Roncato",
        "endereco": "Rua Nair Santos Cunhas, 371 - Distr. Industrial Waldemar de Oliveira Verdi",
        "email": "contato@ferrovelhoroncato.com.br",
        "site": "https://ferrovelhoroncato.com.br/",
        "cnpj": "17.449.814/0001-00",
    }

def carregar_materiais(tenant=None):
    """Carregar materiais disponíveis"""
    try:
        if tenant:
            materiais = SucataMaterial.objects.filter(tenant=tenant, is_active=True)
            return [(mat.nome, mat.preco_atual) for mat in materiais.order_by('categoria', 'order')]
        else:
            # Lista padrão para desenvolvimento
            return [
                ("Chaparia", 0.80), ("Miúda", 0.75), ("Estamparia", 0.85), ("Fundido", 0.90),
                ("Cavaco", 0.70), ("Mola escolha", 1.20), ("Filtro óleo", 0.50),
                ("Alumínio - Latinha", 4.50), ("Alumínio - Chaparia", 3.80), ("Alumínio - Bloco", 4.20),
                ("Alumínio - Panela", 3.50), ("Alumínio - Perfil Novo", 5.00), ("Alumínio - Perfil Pintado", 4.80),
                ("Alumínio - Radiador", 4.00), ("Alumínio - Roda", 6.00), ("Alumínio - Cavaco", 3.00),
                ("Alumínio - Estamparia", 3.50), ("Alumínio - Off-set", 4.50), ("Bateria", 2.50),
                ("Chumbo", 3.20), ("Cobre - Mel", 25.00), ("Cobre - Misto", 22.00),
                ("Radiador Alum. Cobre", 18.00), ("Cobre Encapado", 20.00), ("Metal Latão", 12.00),
                ("Cavaco Metal", 8.00), ("Radiador Metal", 15.00), ("Bronze", 14.00),
                ("Cavaco Bronze", 10.00), ("Inox 304", 8.00), ("Inox 430", 6.50),
                ("Material Sujo", 0.30), ("Magnésio", 5.00), ("Antimônio", 8.00)
            ]
    except:
        # Fallback para lista padrão
        return [
            ("Chaparia", 0.80), ("Miúda", 0.75), ("Estamparia", 0.85),
            ("Alumínio - Latinha", 4.50), ("Bateria", 2.50), ("Cobre - Mel", 25.00)
        ]

def salvar_entrada_sucata(tenant, cliente, observacoes, materiais_quantidades):
    """Salvar entrada de sucata no banco Django"""
    try:
        # Criar entrada
        entrada = SucataEntry.objects.create(
            tenant=tenant,
            cliente=cliente,
            observacoes=observacoes,
            created_by=None  # Será definido pelo middleware de autenticação
        )

        # Criar itens
        for material_nome, quantidade in materiais_quantidades.items():
            if quantidade > 0:
                try:
                    material = SucataMaterial.objects.get(
                        tenant=tenant,
                        nome=material_nome,
                        is_active=True
                    )

                    SucataItem.objects.create(
                        entrada=entrada,
                        material=material,
                        quantidade=quantidade,
                        valor_unitario=material.preco_atual
                    )
                except SucataMaterial.DoesNotExist:
                    # Criar material se não existir
                    material = SucataMaterial.objects.create(
                        tenant=tenant,
                        nome=material_nome,
                        categoria="Diversos",
                        preco_base=1.00,
                        preco_atual=1.00
                    )

                    SucataItem.objects.create(
                        entrada=entrada,
                        material=material,
                        quantidade=quantidade,
                        valor_unitario=1.00
                    )

        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def carregar_entradas_sucata(tenant=None):
    """Carregar entradas de sucata do banco Django"""
    try:
        if tenant:
            entradas = SucataEntry.objects.filter(tenant=tenant).order_by('-data', '-hora')
            dados = []

            for entrada in entradas:
                linha = {
                    'Cliente': entrada.cliente,
                    'Data': entrada.data.strftime('%Y-%m-%d'),
                    'Hora': entrada.hora.strftime('%H:%M:%S'),
                    'Observações': entrada.observacoes or '',
                }

                # Adicionar materiais
                for item in entrada.items.all():
                    linha[item.material.nome] = float(item.quantidade)

                dados.append(linha)

            return pd.DataFrame(dados) if dados else pd.DataFrame()
        else:
            # Dados de exemplo para desenvolvimento
            return pd.DataFrame([{
                'Cliente': 'Cliente Exemplo',
                'Data': datetime.now().strftime('%Y-%m-%d'),
                'Hora': datetime.now().strftime('%H:%M:%S'),
                'Observações': 'Entrada de exemplo',
                'Chaparia': 10.0,
                'Alumínio - Latinha': 5.0
            }])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def gerar_pdf_empresa(df, company_info, filename="relatorio.pdf"):
    """Gerar PDF com informações da empresa"""
    pdf = FPDF()
    pdf.add_page()

    # Logo se existir
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, 10, 8, 33)

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Controle de Sucata", ln=True, align="C")
    pdf.ln(10)

    # Informações da empresa
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 8, company_info["nome"], ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 6, company_info["endereco"], ln=True, align="C")
    pdf.cell(200, 6, f"{company_info['email']} | {company_info['site']}", ln=True, align="C")
    pdf.cell(200, 6, f"CNPJ: {company_info['cnpj']}", ln=True, align="C")
    pdf.ln(10)

    # Dados das entradas
    pdf.set_font("Arial", "", 9)
    for _, row in df.iterrows():
        linha = f"{row['Data']} {row['Hora']} | Cliente: {row['Cliente']}"
        if row.get('Observações'):
            linha += f" | Obs: {row['Observações']}"
        pdf.multi_cell(0, 6, linha)

        # Mostrar materiais
        materiais = {k: v for k, v in row.items() if k not in ["Cliente", "Data", "Hora", "Observações"] and v > 0}
        if materiais:
            for mat, qtd in materiais.items():
                pdf.cell(10)
                pdf.cell(0, 6, f"  • {mat}: {qtd}kg", ln=True)

        pdf.ln(3)

    # Rodapé
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(200, 5, f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")

    pdf.output(filename)
    return filename

# --- Layout Principal ---
def main():
    st.set_page_config(
        page_title="Ferro Velho - Controle de Sucata",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Obter tenant
    tenant = get_tenant_from_session()
    company_info = get_company_info(tenant)

    # Sidebar com informações da empresa
    with st.sidebar:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=100)

        st.title(f"🏭 {company_info['nome']}")

        st.markdown("### 📍 Informações")
        st.info(f"📧 {company_info['email']}")
        st.info(f"🌐 {company_info['site']}")
        st.info(f"🏢 CNPJ: {company_info['cnpj']}")

        if tenant:
            st.success(f"✅ Tenant: {tenant.name}")
        else:
            st.warning("⚠️ Modo desenvolvimento (sem tenant)")

        st.markdown("---")
        st.markdown("### 📚 Recursos")
        st.markdown("- [📖 Documentação](https://docs.aviladevops.com.br)")
        st.markdown("- [💬 Suporte](mailto:suporte@aviladevops.com.br)")
        st.markdown("- [🔗 Site Oficial](https://aviladevops.com.br)")

    # Título principal
    st.title("📲 Controle de Sucata - Ferro Velho")

    if not tenant:
        st.warning("⚠️ Executando em modo desenvolvimento. Configure um tenant para usar todos os recursos.")

    # Abas principais
    tab1, tab2, tab3 = st.tabs(["➕ Nova Entrada", "📋 Registros", "📊 Relatórios"])

    # --- Aba 1: Nova Entrada ---
    with tab1:
        st.header("Nova Entrada de Sucata")

        with st.form("entrada_sucata"):
            col1, col2 = st.columns(2)

            with col1:
                cliente = st.text_input("Cliente", placeholder="Nome do cliente/fornecedor")
                observacoes = st.text_area("Observações", placeholder="Observações sobre a entrada...")

            with col2:
                st.markdown("### 📅 Data e Hora")
                data = st.date_input("Data", datetime.now())
                hora = st.time_input("Hora", datetime.now())

            st.markdown("---")
            st.markdown("### ⚖️ Materiais (kg)")

            # Carregar materiais
            materiais = carregar_materiais(tenant)

            # Dividir materiais em colunas
            col1, col2, col3 = st.columns(3)

            quantidades = {}
            for i, (material_nome, preco) in enumerate(materiais):
                col = [col1, col2, col3][i % 3]

                with col:
                    quantidades[material_nome] = st.number_input(
                        f"{material_nome} (R$ {preco:.2f})"
                        min_value=0.0,
                        step=0.1,
                        key=f"mat_{i}"
                    )

            submitted = st.form_submit_button("💾 Salvar Entrada", use_container_width=True)

            if submitted:
                if not cliente.strip():
                    st.error("❌ Cliente é obrigatório!")
                else:
                    # Filtrar materiais com quantidade > 0
                    materiais_selecionados = {k: v for k, v in quantidades.items() if v > 0}

                    if not materiais_selecionados:
                        st.error("❌ Selecione pelo menos um material!")
                    else:
                        # Salvar no banco
                        sucesso = salvar_entrada_sucata(
                            tenant,
                            cliente,
                            observacoes,
                            materiais_selecionados
                        )

                        if sucesso:
                            st.success("✅ Entrada salva com sucesso!")
                            st.balloons()

                            # Mostrar resumo
                            with st.expander("📋 Resumo da Entrada"):
                                st.write(f"**Cliente:** {cliente}")
                                st.write(f"**Data/Hora:** {data} {hora}")
                                st.write(f"**Observações:** {observacoes or 'Nenhuma'}")

                                total_kg = sum(materiais_selecionados.values())
                                st.write(f"**Total:** {total_kg:.1f}kg")                                # Calcular valor estimado
                                valor_total = sum(qtd * next(p for m, p in materiais if m == mat) for mat, qtd in materiais_selecionados.items())
                                st.write(f"**Valor estimado:** R$ {valor_total:.2f}")
    # --- Aba 2: Registros ---
    with tab2:
        st.header("Registros de Entradas")

        df = carregar_entradas_sucata(tenant)

        if not df.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)

            with col1:
                clientes_unicos = ["Todos"] + df["Cliente"].dropna().unique().tolist()
                filtro_cliente = st.selectbox("Filtrar por cliente", clientes_unicos)

            with col2:
                filtro_data = st.date_input("Filtrar por data (início)", datetime.now())

            with col3:
                mostrar_todos = st.checkbox("Mostrar todos os registros", value=True)

            # Aplicar filtros
            df_filtrado = df.copy()
            if filtro_cliente != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Cliente"] == filtro_cliente]

            if not mostrar_todos:
                df_filtrado = df_filtrado[df_filtrado["Data"] >= filtro_data.strftime("%Y-%m-%d")]

            # Mostrar registros
            for idx, row in df_filtrado.iterrows():
                with st.expander(f"📦 {row['Data']} {row['Hora']} - Cliente: {row['Cliente']}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Observações:** {row.get('Observações', 'Nenhuma')}")

                    with col2:
                        st.write("**Materiais:**")
                        materiais = {k: v for k, v in row.items()
                                   if k not in ["Cliente", "Data", "Hora", "Observações"] and v > 0}
                        if materiais:
                            for mat, qtd in materiais.items():
                                st.write(f"• {mat}: {qtd}kg")
                        else:
                            st.write("Nenhum material informado")

                    # Botões de ação
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Editar", key=f"edit_{idx}"):
                            st.info("Funcionalidade em desenvolvimento")
                    with col2:
                        if st.button("🖨️ Imprimir", key=f"print_{idx}"):
                            st.info("Funcionalidade em desenvolvimento")
                    with col3:
                        if st.button("❌ Excluir", key=f"delete_{idx}"):
                            st.error("Funcionalidade em desenvolvimento")
        else:
            st.info("📭 Nenhum registro encontrado.")

            # Botão para importar dados antigos
            if st.button("📥 Importar dados antigos (CSV)"):
                st.info("Funcionalidade em desenvolvimento")

    # --- Aba 3: Relatórios ---
    with tab3:
        st.header("Relatórios e Análises")

        df = carregar_entradas_sucata(tenant)

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📊 Estatísticas Gerais")
                total_entradas = len(df)
                total_clientes = df["Cliente"].nunique()
                periodo = f"{df['Data'].min()} a {df['Data'].max()}"

                st.metric("Total de Entradas", total_entradas)
                st.metric("Clientes Únicos", total_clientes)
                st.info(f"📅 Período: {periodo}")

            with col2:
                st.markdown("### 💰 Totais por Categoria")

                # Calcular totais por categoria (simplificado)
                materiais_cols = [col for col in df.columns if col not in ["Cliente", "Data", "Hora", "Observações"]]
                totais = df[materiais_cols].sum().sort_values(ascending=False)

                for material, total in totais.head(5).items():
                    if total > 0:
                        st.metric(f"Total {material}", f"{total:.1f}kg")
            # Filtros para relatório
            st.markdown("---")
            st.markdown("### 📑 Gerar Relatório")

            filtro_cliente_rel = st.selectbox(
                "Cliente (opcional)",
                ["Todos"] + df["Cliente"].dropna().unique().tolist(),
                key="rel_cliente"
            )

            filtro_data_inicio = st.date_input("Data início", df["Data"].min(), key="rel_data_ini")
            filtro_data_fim = st.date_input("Data fim", df["Data"].max(), key="rel_data_fim")

            # Aplicar filtros ao relatório
            df_relatorio = df.copy()
            if filtro_cliente_rel != "Todos":
                df_relatorio = df_relatorio[df_relatorio["Cliente"] == filtro_cliente_rel]

            df_relatorio = df_relatorio[
                (df_relatorio["Data"] >= filtro_data_inicio.strftime("%Y-%m-%d")) &
                (df_relatorio["Data"] <= filtro_data_fim.strftime("%Y-%m-%d"))
            ]

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 Gerar Relatório PDF", use_container_width=True):
                    with st.spinner("Gerando PDF..."):
                        filename = gerar_pdf_empresa(df_relatorio, company_info)
                        with open(filename, "rb") as f:
                            st.download_button(
                                "⬇️ Baixar PDF",
                                f,
                                filename,
                                use_container_width=True
                            )

            with col2:
                if st.button("📈 Exportar Excel", use_container_width=True):
                    # Criar arquivo Excel
                    excel_buffer = df_relatorio.to_excel(index=False)
                    st.download_button(
                        "⬇️ Baixar Excel",
                        excel_buffer,
                        "relatorio_sucata.xlsx",
                        use_container_width=True
                    )

            # Prévia do relatório
            if not df_relatorio.empty:
                with st.expander("👁️ Prévia do Relatório"):
                    st.dataframe(df_relatorio, use_container_width=True)

                        # Estatísticas do período
                        st.markdown("#### 📈 Estatísticas do Período")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Entradas", len(df_relatorio))

                        with col2:
                            total_kg = df_relatorio.select_dtypes(include=[float]).sum().sum()
                            st.metric("Total (kg)", f"{total_kg:.1f}")
                        with col3:
                            valor_est = total_kg * 2.50  # Estimativa média
                            st.metric("Valor Est. (R$)", f"{valor_est:.2f}")
        else:
            st.warning("⚠️ Nenhum dado disponível para relatório.")

            # Botão para popular dados de exemplo
            if st.button("🎲 Gerar Dados de Exemplo"):
                st.info("Funcionalidade em desenvolvimento")

    # --- Rodapé ---
    st.markdown("---")
    st.caption(f"🏭 {company_info['nome']} | 📧 {company_info['email']} | 🌐 {company_info['site']}")
    st.caption("Desenvolvido pela Ávila DevOps | Sistema integrado ao SaaS Multi-tenant")


if __name__ == "__main__":
    main()
