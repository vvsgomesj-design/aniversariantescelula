import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import urllib.parse

# 1. CONFIGURAÇÕES E ESTILOS
st.set_page_config(page_title="Aniversariantes - Sonho Dourado", page_icon="🎉", layout="wide")

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DIRETORIO_ATUAL, "membros_sonho_dourado.json")

MESES_MAP = {
    "Todos": "Todos", "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
    "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
    "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
}

# 2. FUNÇÕES DE APOIO
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

# Inicialização do Estado
if 'df_membros' not in st.session_state:
    st.session_state.df_membros = carregar_dados()

st.title("🎂 Aniversariantes - Sonho Dourado")

# --- 3. BLOCO DE NOVO CADASTRO (O que faltava) ---
with st.expander("➕ Adicionar Novo Membro à Célula"):
    with st.form("novo_cadastro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome_n = c1.text_input("Nome Completo")
        whats_n = c2.text_input("WhatsApp (com DDD)")
        
        c3, c4 = st.columns(2)
        niver_n = c3.text_input("Data de Aniversário (Ex: 28/06)")
        gen_n = c4.selectbox("Gênero", ["Feminino", "Masculino"])
        
        if st.form_submit_button("✨ Cadastrar na Lista"):
            if nome_n and niver_n:
                novo_membro = pd.DataFrame([{"Nome": nome_n, "WhatsApp": whats_n, "Aniversario": niver_n, "Genero": gen_n}])
                st.session_state.df_membros = pd.concat([st.session_state.df_membros, novo_membro], ignore_index=True)
                salvar_dados(st.session_state.df_membros)
                st.success(f"✅ {nome_n} adicionado com sucesso!")
                st.rerun()
            else:
                st.error("⚠️ Por favor, preencha pelo menos Nome e Data.")

# --- 4. BANNER DE HOJE ---
hoje = datetime.now().strftime("%d/%m")
df_atual = st.session_state.df_membros
niver_hoje = df_atual[df_atual['Aniversario'].str.strip() == hoje]

if not niver_hoje.empty:
    st.markdown("""<div style='background-color:#fef9e7;padding:20px;border-radius:15px;text-align:center;border:2px solid #f1c40f;'>
                <h1 style='margin:0;'>🥳 ANIVERSARIANTES DE HOJE! 🎆</h1></div>""", unsafe_allow_html=True)
    st.balloons()
    for _, row in niver_hoje.iterrows():
        cn, cw = st.columns([3, 1])
        cn.subheader(f"✨ {row['Nome']}")
        link_w = limpar_whatsapp(row['WhatsApp'])
        if link_w: cw.link_button("📱 Parabenizar", link_w, use_container_width=True)
st.divider()

# --- 5. FILTROS ---
st.sidebar.header("🔍 Filtros")
f_nome = st.sidebar.text_input("Buscar por Nome")
f_gen = st.sidebar.multiselect("Gênero", ["Masculino", "Feminino"], default=["Masculino", "Feminino"])
escolha_mes = st.sidebar.selectbox("Mês", list(MESES_MAP.keys()))
f_mes_num = MESES_MAP[escolha_mes]

df_f = df_atual.copy()
df_f = df_f[df_f['Nome'].str.contains(f_nome, case=False, na=False)]
df_f = df_f[df_f['Genero'].isin(f_gen)]
if f_mes_num != "Todos":
    df_f = df_f[df_f['Aniversario'].str.contains(f"/{f_mes_num}", na=False)]

# --- 6. LISTA DE GESTÃO ---
st.subheader(f"📋 Lista: {escolha_mes} ({len(df_f)} pessoas)")

for idx, row in df_f.iterrows():
    icone, cor = ("🧔‍♂️", "#3498db") if row['Genero'] == "Masculino" else ("👗", "#e91e63")
    
    with st.container():
        c1, c2, c3, c4, c5, c6 = st.columns([3, 3, 2, 2, 1, 1])
        c1.write(f"**{row['Nome']}**")
        c2.markdown(f"📅 {row['Aniversario']} | <span style='color:{cor}; font-weight:bold;'>{icone}</span>", unsafe_allow_html=True)
        
        # Ações
        l_a = gerar_link_agenda(row['Nome'], row['Aniversario'])
        if l_a: c3.link_button("📅 Agenda", l_a, use_container_width=True)
        
        l_w = limpar_whatsapp(row['WhatsApp'])
        if l_w: c4.link_button("📱 WhatsApp", l_w, use_container_width=True)
        
        if c5.button("📝", key=f"ed_{idx}"): st.session_state.edit_idx = idx
        if c6.button("🗑️", key=f"del_{idx}"):
            st.session_state.df_membros = st.session_state.df_membros.drop(idx).reset_index(drop=True)
            salvar_dados(st.session_state.df_membros)
            st.rerun()
        st.divider()

# --- 7. MODAL DE EDIÇÃO ---
if 'edit_idx' in st.session_state:
    idx = st.session_state.edit_idx
    m = st.session_state.df_membros.iloc[idx]
    with st.form("edit_form"):
        st.subheader(f"Editar: {m['Nome']}")
        en = st.text_input("Nome", m['Nome'])
        ew = st.text_input("WhatsApp", m['WhatsApp'])
        ea = st.text_input("Data (DD/MM)", m['Aniversario'])
        eg = st.selectbox("Gênero", ["Feminino", "Masculino"], index=0 if m['Genero'] == "Feminino" else 1)
        if st.form_submit_button("Salvar Alterações"):
            st.session_state.df_membros.at[idx, 'Nome'] = en
            st.session_state.df_membros.at[idx, 'WhatsApp'] = ew
            st.session_state.df_membros.at[idx, 'Aniversario'] = ea
            st.session_state.df_membros.at[idx, 'Genero'] = eg
            salvar_dados(st.session_state.df_membros)
            del st.session_state.edit_idx
            st.rerun()