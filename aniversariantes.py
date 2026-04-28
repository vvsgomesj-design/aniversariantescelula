import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import urllib.parse

# 1. CONFIGURAÇÕES E ESTILOS GIGANTES (CSS)
st.set_page_config(page_title="Sonho Dourado", page_icon="🎉", layout="wide")

st.markdown("""
    <style>
    /* Nome do Membro - Tamanho Extra Grande */
    .nome-membro {
        font-size: 28px !important;
        font-weight: 800;
        color: #1E1E1E;
        margin-bottom: 2px;
        line-height: 1.2;
    }
    /* Data e Gênero - Tamanho Grande */
    .info-membro {
        font-size: 22px !important;
        color: #444;
        margin-bottom: 10px;
    }
    /* Forçar botões lado a lado no celular */
    .stButton button {
        font-size: 20px !important;
        padding: 10px 0px !important;
        border-radius: 10px;
    }
    /* Remove espaçamentos inúteis entre colunas */
    [data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 50px !important;
        padding: 0px 3px !important;
    }
    hr {
        margin-top: 15px !important;
        margin-bottom: 15px !important;
        border: 0;
        border-top: 2px solid #EEE;
    }
    </style>
    """, unsafe_allow_html=True)

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DIRETORIO_ATUAL, "membros_sonho_dourado.json")

MESES_MAP = {
    "Todos": "Todos", "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
    "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
    "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
}

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f)).fillna('')
    return pd.DataFrame(columns=["Nome", "WhatsApp", "Aniversario", "Genero"])

def salvar_dados(df):
    df.to_json(DB_FILE, orient="records", force_ascii=False, indent=4)

def limpar_whatsapp(numero):
    num = "".join(filter(str.isdigit, str(numero)))
    if num:
        if not num.startswith("55"): num = "55" + num
        return f"https://wa.me/{num}"
    return None

def gerar_link_agenda(nome, data_br):
    if not data_br or '/' not in data_br: return None
    dia, mes = data_br.split('/')
    ano_atual = datetime.now().year
    data_formatada = f"{ano_atual}{mes}{dia}"
    link = f"https://www.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote('🎂 ' + nome)}&dates={data_formatada}/{data_formatada}&recur=RRULE:FREQ=YEARLY&sf=true&output=xml"
    return link

if 'df_membros' not in st.session_state:
    st.session_state.df_membros = carregar_dados()

st.title("🎂 Sonho Dourado")

# --- CADASTRO ---
with st.expander("➕ Adicionar Pessoa"):
    with st.form("novo_cadastro", clear_on_submit=True):
        nome_n = st.text_input("Nome")
        whats_n = st.text_input("WhatsApp")
        niver_n = st.text_input("Aniversário (Ex: 28/06)")
        gen_n = st.selectbox("Gênero", ["Feminino", "Masculino"])
        if st.form_submit_button("Cadastrar"):
            if nome_n and niver_n:
                novo = pd.DataFrame([{"Nome": nome_n, "WhatsApp": whats_n, "Aniversario": niver_n, "Genero": gen_n}])
                st.session_state.df_membros = pd.concat([st.session_state.df_membros, novo], ignore_index=True)
                salvar_dados(st.session_state.df_membros)
                st.rerun()

# --- FILTROS ---
st.sidebar.header("🔍 Filtros")
f_nome = st.sidebar.text_input("Buscar Nome")
escolha_mes = st.sidebar.selectbox("Mês", list(MESES_MAP.keys()))
f_mes_num = MESES_MAP[escolha_mes]

df_f = st.session_state.df_membros.copy()
df_f = df_f[df_f['Nome'].str.contains(f_nome, case=False, na=False)]
if f_mes_num != "Todos":
    df_f = df_f[df_f['Aniversario'].str.contains(f"/{f_mes_num}", na=False)]

# --- LISTA SUPER LEGÍVEL ---
st.subheader(f"📋 {escolha_mes}")

for idx, row in df_f.iterrows():
    icone, cor = ("🧔‍♂️", "#3498db") if row['Genero'] == "Masculino" else ("👗", "#e91e63")
    
    # Nome GIGANTE
    st.markdown(f"<div class='nome-membro'>{row['Nome']}</div>", unsafe_allow_html=True)
    # Data e Ícone Grandes
    st.markdown(f"<div class='info-membro'>📅 {row['Aniversario']} | <span style='color:{cor}'>{icone}</span></div>", unsafe_allow_html=True)
    
    # Botões na mesma linha (4 colunas)
    b1, b2, b3, b4 = st.columns(4)
    
    # WhatsApp
    l_w = limpar_whatsapp(row['WhatsApp'])
    if l_w: b1.link_button("📱", l_w)
    
    # Agenda
    l_a = gerar_link_agenda(row['Nome'], row['Aniversario'])
    if l_a: b2.link_button("📅", l_a)
    
    # Editar
    if b3.button("📝", key=f"ed_{idx}"):
        st.session_state.edit_idx = idx
        st.rerun()
        
    # Lixo
    if b4.button("🗑️", key=f"del_{idx}"):
        st.session_state.df_membros = st.session_state.df_membros.drop(idx).reset_index(drop=True)
        salvar_dados(st.session_state.df_membros)
        st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)

# --- EDIÇÃO ---
if 'edit_idx' in st.session_state:
    idx = st.session_state.edit_idx
    m = st.session_state.df_membros.iloc[idx]
    with st.form("edit_form"):
        st.write("### Editar Registro")
        en = st.text_input("Nome", m['Nome'])
        ew = st.text_input("WhatsApp", m['WhatsApp'])
        ea = st.text_input("Data", m['Aniversario'])
        eg = st.selectbox("Gênero", ["Feminino", "Masculino"], index=0 if m['Genero'] == "Feminino" else 1)
        if st.form_submit_button("Salvar"):
            st.session_state.df_membros.at[idx, 'Nome'] = en
            st.session_state.df_membros.at[idx, 'WhatsApp'] = ew
            st.session_state.df_membros.at[idx, 'Aniversario'] = ea
            st.session_state.df_membros.at[idx, 'Genero'] = eg
            salvar_dados(st.session_state.df_membros)
            del st.session_state.edit_idx
            st.rerun()