import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import urllib.parse

# 1. CONFIGURAÇÕES E ESTILOS CUSTOMIZADOS (CSS)
st.set_page_config(page_title="Sonho Dourado", page_icon="🎉", layout="wide")

# CSS para aumentar as fontes e ajustar botões no celular
st.markdown("""
    <style>
    .nome-membro {
        font-size: 22px !important;
        font-weight: bold;
        margin-bottom: -5px;
    }
    .info-membro {
        font-size: 18px !important;
        color: #555;
    }
    .stButton button {
        width: 100%;
        padding: 5px;
    }
    /* Ajuste para botões ficarem mais próximos */
    [data-testid="column"] {
        padding: 0px 5px !important;
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
    link = f"https://www.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote('🎂 Aniversário: ' + nome)}&dates={data_formatada}/{data_formatada}&recur=RRULE:FREQ=YEARLY&sf=true&output=xml"
    return link

if 'df_membros' not in st.session_state:
    st.session_state.df_membros = carregar_dados()

st.title("🎂 Sonho Dourado")

# --- CADASTRO ---
with st.expander("➕ Novo Membro"):
    with st.form("novo_cadastro", clear_on_submit=True):
        nome_n = st.text_input("Nome")
        c1, c2 = st.columns(2)
        whats_n = c1.text_input("Zap")
        niver_n = c2.text_input("Data (DD/MM)")
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

# --- LISTA ESTILIZADA ---
st.subheader(f"📋 {escolha_mes}")

for idx, row in df_f.iterrows():
    icone, cor = ("🧔‍♂️", "#3498db") if row['Genero'] == "Masculino" else ("👗", "#e91e63")
    
    # Nome e Data com fontes grandes
    st.markdown(f"<div class='nome-membro'>{row['Nome']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-membro'>📅 {row['Aniversario']} | <span style='color:{cor}'>{icone}</span></div>", unsafe_allow_html=True)
    
    # Botões Lado a Lado (4 colunas pequenas)
    b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
    
    l_a = gerar_link_agenda(row['Nome'], row['Aniversario'])
    if l_a: b1.link_button("📅", l_a, help="Agenda")
    
    l_w = limpar_whatsapp(row['WhatsApp'])
    if l_w: b2.link_button("📱", l_w, help="WhatsApp")
    
    if b3.button("📝", key=f"ed_{idx}"):
        st.session_state.edit_idx = idx
        st.rerun()
        
    if b4.button("🗑️", key=f"del_{idx}"):
        st.session_state.df_membros = st.session_state.df_membros.drop(idx).reset_index(drop=True)
        salvar_dados(st.session_state.df_membros)
        st.rerun()
    
    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# --- EDIÇÃO ---
if 'edit_idx' in st.session_state:
    idx = st.session_state.edit_idx
    m = st.session_state.df_membros.iloc[idx]
    with st.form("edit_form"):
        en = st.text_input("Nome", m['Nome'])
        ea = st.text_input("Data", m['Aniversario'])
        eg = st.selectbox("Gênero", ["Feminino", "Masculino"], index=0 if m['Genero'] == "Feminino" else 1)
        if st.form_submit_button("Salvar"):
            st.session_state.df_membros.at[idx, 'Nome'] = en
            st.session_state.df_membros.at[idx, 'Aniversario'] = ea
            st.session_state.df_membros.at[idx, 'Genero'] = eg
            salvar_dados(st.session_state.df_membros)
            del st.session_state.edit_idx
            st.rerun()