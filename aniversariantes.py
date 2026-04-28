import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import urllib.parse

# 1. CONFIGURAÇÕES E ESTILOS
st.set_page_config(page_title="Sonho Dourado", page_icon="🎉", layout="wide")

st.markdown("""
    <style>
    .nome-membro { font-size: 24px !important; font-weight: bold; margin-bottom: -5px; }
    .info-membro { font-size: 19px !important; color: #555; }
    .banner-festa { background-color: #fef9e7; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #f1c40f; margin: 20px 0; }
    .stButton button { width: 100%; padding: 8px; font-size: 18px; }
    hr { margin: 15px 0; }
    </style>
    """, unsafe_allow_html=True)

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DIRETORIO_ATUAL, "membros_sonho_dourado.json")

MESES_MAP = {
    "Todos os Meses": "Todos", "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
    "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
    "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
}

# 2. FUNÇÕES
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
    ano_at = datetime.now().year
    dt = f"{ano_at}{mes}{dia}"
    return f"https://www.google.com/calendar/render?action=TEMPLATE&text={urllib.parse.quote('🎂 Aniversário: '+nome)}&dates={dt}/{dt}&recur=RRULE:FREQ=YEARLY&sf=true&output=xml"

def gerar_arquivo_ics(df):
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//SonhoDourado//PT\n"
    ano_at = datetime.now().year
    for _, r in df.iterrows():
        if r['Aniversario'] and '/' in r['Aniversario']:
            d, m = r['Aniversario'].split('/')
            ics_content += f"BEGIN:VEVENT\nSUMMARY:🎂 Aniversário {r['Nome']}\nDTSTART;VALUE=DATE:{ano_at}{m}{d}\nRRULE:FREQ=YEARLY\nEND:VEVENT\n"
    ics_content += "END:VCALENDAR"
    return ics_content

if 'df_membros' not in st.session_state:
    st.session_state.df_membros = carregar_dados()

# --- TÍTULO PRINCIPAL ---
st.title("🎉 Sonho Dourado")

# --- 3. CADASTRO (DIRETO NA TELA) ---
st.subheader("➕ Novo Membro")
with st.form("novo_cadastro", clear_on_submit=True):
    nome_n = st.text_input("Nome Completo")
    c1, c2, c3 = st.columns(3)
    whats_n = c1.text_input("WhatsApp")
    niver_n = c2.text_input("Data (DD/MM)")
    gen_n = c3.selectbox("Gênero", ["Feminino", "Masculino"])
    
    if st.form_submit_button("💾 Salvar Novo Membro"):
        if nome_n and niver_n:
            novo = pd.DataFrame([{"Nome": nome_n, "WhatsApp": whats_n, "Aniversario": niver_n, "Genero": gen_n}])
            st.session_state.df_membros = pd.concat([st.session_state.df_membros, novo], ignore_index=True)
            salvar_dados(st.session_state.df_membros)
            st.success(f"{nome_n} adicionado!")
            st.rerun()

st.divider()

# --- 4. FILTROS (DIRETO NA TELA - SEM SIDEBAR) ---
st.subheader("🔍 Localizar Membro")
col_f1, col_f2 = st.columns(2)
f_nome = col_f1.text_input("Pesquisar por Nome")
escolha_mes = col_f2.selectbox("Filtrar por Mês", list(MESES_MAP.keys()))
f_mes_num = MESES_MAP[escolha_mes]

# Lógica de Filtro
df_total = st.session_state.df_membros
df_f = df_total.copy()
df_f = df_f[df_f['Nome'].str.contains(f_nome, case=False, na=False)]
if f_mes_num != "Todos":
    df_f = df_f[df_f['Aniversario'].str.contains(f"/{f_mes_num}", na=False)]

st.divider()

# --- 5. BANNER DE HOJE ---
hoje = datetime.now().strftime("%d/%m")
niver_hoje = df_total[df_total['Aniversario'].str.strip() == hoje]

if not niver_hoje.empty:
    st.markdown('<div class="banner-festa"><h2>🥳 ANIVERSARIANTES DE HOJE!</h2></div>', unsafe_allow_html=True)
    st.balloons()
    for _, row in niver_hoje.iterrows():
        cn, cw = st.columns([2, 1])
        cn.markdown(f"#### ✨ {row['Nome']}")
        lw = limpar_whatsapp(row['WhatsApp'])
        if lw: cw.link_button("📱 Dar Parabéns", lw)
    st.divider()

# --- 6. LISTA DE MEMBROS ---
st.subheader(f"📋 Exibindo: {escolha_mes}")

if df_f.empty:
    st.info("Nenhum membro encontrado com esses filtros.")
else:
    for idx, row in df_f.iterrows():
        ic, cor = ("🧔‍♂️", "#3498db") if row['Genero'] == "Masculino" else ("👗", "#e91e63")
        
        st.markdown(f"<div class='nome-membro'>{row['Nome']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-membro'>📅 {row['Aniversario']} | <span style='color:{cor}'>{ic}</span></div>", unsafe_allow_html=True)
        
        b1, b2, b3, b4 = st.columns(4)
        la = gerar_link_agenda(row['Nome'], row['Aniversario'])
        if la: b1.link_button("📅", la)
        lw = limpar_whatsapp(row['WhatsApp'])
        if lw: b2.link_button("📱", lw)
        if b3.button("📝", key=f"e_{idx}"): 
            st.session_state.edit_idx = idx
            st.rerun()
        if b4.button("🗑️", key=f"d_{idx}"):
            st.session_state.df_membros = st.session_state.df_membros.drop(idx).reset_index(drop=True)
            salvar_dados(st.session_state.df_membros)
            st.rerun()
        st.markdown("<hr>", unsafe_allow_html=True)

# --- 7. EXPORTAÇÃO GERAL ---
st.subheader("🚀 Configuração Geral")
st.write("Adicione todos os aniversários da célula à sua agenda de uma só vez:")
ics_data = gerar_arquivo_ics(df_total)
st.download_button(
    label="📥 ADICIONAR TODOS À AGENDA",
    data=ics_data,
    file_name="agenda_sonho_dourado.ics",
    mime="text/calendar",
    use_container_width=True
)

# --- EDIÇÃO ---
if 'edit_idx' in st.session_state:
    idx = st.session_state.edit_idx
    m = st.session_state.df_membros.iloc[idx]
    with st.form("edit_form"):
        st.write(f"### Editando: {m['Nome']}")
        en = st.text_input("Nome", m['Nome'])
        ew = st.text_input("Zap", m['WhatsApp'])
        ea = st.text_input("Data", m['Aniversario'])
        eg = st.selectbox("Gênero", ["Feminino", "Masculino"], index=0 if m['Genero'] == "Feminino" else 1)
        if st.form_submit_button("Salvar Alterações"):
            st.session_state.df_membros.at[idx, 'Nome'] = en
            st.session_state.df_membros.at[idx, 'WhatsApp'] = ew
            st.session_state.df_membros.at[idx, 'Aniversario'] = ea
            st.session_state.df_membros.at[idx, 'Genero'] = eg
            salvar_dados(st.session_state.df_membros)
            del st.session_state.edit_idx
            st.rerun()