import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# --- Configurações ---
DATA_FILE = "entradas_sucata.csv"
LOGO_FILE = "logo.png"

# --- Dados da empresa ---
INFO_EMPRESA = {
    "endereco": "Rua Nair Santos Cunhas, 371 - Distr. Industrial Waldemar de Oliveira Verdi",
    "email": "contato@ferrovelhoroncato.com.br",
    "site": "https://ferrovelhoroncato.com.br/",
    "cnpj": "17.449.814/0001-00",
}

# --- Funções ---
def carregar_dados():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame()

def salvar_registro(registro):
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def gerar_pdf(df, filename="relatorio.pdf"):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, 10, 8, 33)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Controle de Sucata", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 10)
    for _, row in df.iterrows():
        linha = f"{row['Data']} {row['Hora']} | Cliente: {row['Cliente']} | Obs: {row['Observações']}"
        pdf.multi_cell(0, 8, linha)
    pdf.ln(10)

    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 6,
        f"{INFO_EMPRESA['endereco']} | {INFO_EMPRESA['email']} | {INFO_EMPRESA['site']} | CNPJ: {INFO_EMPRESA['cnpj']}"
    )
    pdf.output(filename)

# --- Layout ---
st.set_page_config(page_title="Ferro Velho Roncato", layout="centered")

if os.path.exists(LOGO_FILE):
    st.image(LOGO_FILE, width=100)

st.title("📲 Controle de Sucata")

abas = st.tabs(["➕ Entrada", "📋 Registros", "📑 Relatórios"])

# --- Aba 1: Entrada ---
with abas[0]:
    st.subheader("Nova Entrada")

    cliente = st.text_input("Cliente")
    observacoes = st.text_area("Observações")
    data = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")

    st.markdown("### Materiais (kg)")
    materiais = [
        "Chaparia", "Miúda", "Estamparia", "Fundido", "Cavaco", "Mola escolha", "Filtro óleo",
        "Alumínio - Latinha", "Alumínio - Chaparia", "Alumínio - Bloco", "Alumínio - Panela",
        "Alumínio - Perfil Novo", "Alumínio - Perfil Pintado", "Alumínio - Radiador",
        "Alumínio - Roda", "Alumínio - Cavaco", "Alumínio - Estamparia", "Alumínio - Off-set",
        "Bateria", "Chumbo", "Cobre - Mel", "Cobre - Misto", "Radiador Alum. Cobre",
        "Cobre Encapado", "Metal Latão", "Cavaco Metal", "Radiador Metal", "Bronze",
        "Cavaco Bronze", "Inox 304", "Inox 430", "Material Sujo", "Magnésio", "Antimônio"
    ]

    quantidades = {}
    for mat in materiais:
        quantidades[mat] = st.number_input(mat, 0.0, step=1.0, key=mat)

    if st.button("💾 Salvar Registro"):
        registro = {"Cliente": cliente, "Data": data, "Hora": hora, "Observações": observacoes}
        registro.update(quantidades)
        salvar_registro(registro)
        st.success("✅ Registro salvo!")

# --- Aba 2: Registros ---
with abas[1]:
    st.subheader("Registros Salvos")
    df = carregar_dados()
    if not df.empty:
        for idx, row in df.iterrows():
            with st.expander(f"{row['Data']} {row['Hora']} - Cliente: {row['Cliente']}"):
                st.write(f"**Observações:** {row['Observações']}")
                materiais = {k: v for k, v in row.items() if k not in ["Cliente", "Data", "Hora", "Observações"]}
                materiais_filtrados = {m: q for m, q in materiais.items() if q > 0}
                if materiais_filtrados:
                    st.table(pd.DataFrame(materiais_filtrados.items(), columns=["Material", "Quantidade (kg)"]))
                else:
                    st.write("Sem materiais informados.")
    else:
        st.info("Nenhum registro encontrado.")

# --- Aba 3: Relatórios ---
with abas[2]:
    st.subheader("Gerar Relatórios")
    df = carregar_dados()
    if not df.empty:
        filtro_cliente = st.selectbox("Filtrar por cliente (opcional)", ["Todos"] + df["Cliente"].dropna().unique().tolist())
        if filtro_cliente != "Todos":
            df = df[df["Cliente"] == filtro_cliente]

        if st.button("📑 Gerar PDF"):
            gerar_pdf(df)
            with open("relatorio.pdf", "rb") as f:
                st.download_button("⬇️ Baixar Relatório PDF", f, "relatorio.pdf")

        st.download_button("⬇️ Baixar Excel", df.to_csv(index=False).encode("utf-8"), "registros.csv")
    else:
        st.warning("Nenhum dado disponível para relatório.")

# --- Rodapé ---
st.markdown("---")
st.caption(
    f"{INFO_EMPRESA['endereco']} | {INFO_EMPRESA['email']} | "
    f"[{INFO_EMPRESA['site']}]({INFO_EMPRESA['site']}) | CNPJ: {INFO_EMPRESA['cnpj']}"
)
st.caption("Desenvolvido por Nícolas Ávila")