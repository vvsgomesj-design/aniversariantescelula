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
    .banner-festa { background-color: #fef9e7; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #f1c40f; margin-bottom: 20px; }
    .stButton button { width: 100%; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DIRETORIO_ATUAL, "membros_sonho_dourado.json")

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
    """Gera um arquivo para importar todos de uma vez"""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    ano_at = datetime.now().year
    for _, r in df.iterrows():
        if r['Aniversario'] and '/' in r['Aniversario']:
            d, m = r['Aniversario'].split('/')
            ics_content += f"BEGIN:VEVENT\nSUMMARY:🎂 Aniversário {r['Nome']}\nDTSTART:{ano_at}{m}{d}\nRRULE:FREQ=YEARLY\nEND:VEVENT\n"
    ics_content += "END:VCALENDAR"
    return ics_content

if 'df_membros' not in st.session_state:
    st.session_state.df_membros = carregar_dados()

st.title("🎉 Sonho Dourado")

# --- BANNER DE HOJE ---
hoje = datetime.now().strftime("%d/%m")
df_at = st.session_state.df_membros
niver_hoje = df_at[df_at['Aniversario'].str.strip() == hoje]

if not niver_hoje.empty:
    st.markdown('<div class="banner-festa"><h1>🥳 HOJE TEM FESTA!</h1></div>', unsafe_allow_html=True)
    st.balloons()
    for _, row in niver_hoje.iterrows():
        c_n, c_w = st.columns([2, 1])
        c_n.markdown(f"### ✨ {row['Nome']}")
        lw = limpar_whatsapp(row['WhatsApp'])
        if lw: c_w.link_button("📱 Parabéns", lw)
    st.divider()

# --- LISTA ---
st.subheader("📋 Lista de Membros")
for idx, row in df_at.iterrows():
    ic, cor = ("🧔‍♂️", "#3498db") if row['Genero'] == "Masculino" else ("👗", "#e91e63")
    st.markdown(f"<div class='nome-membro'>{row['Nome']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-membro'>📅 {row['Aniversario']} | <span style='color:{cor}'>{ic}</span></div>", unsafe_allow_html=True)
    
    b1, b2, b3, b4 = st.columns(4)
    la = gerar_link_agenda(row['Nome'], row['Aniversario'])
    if la: b1.link_button("📅", la)
    lw = limpar_whatsapp(row['WhatsApp'])
    if lw: b2.link_button("📱", lw)
    if b3.button("📝", key=f"e_{idx}"): st.session_state.edit_idx = idx
    if b4.button("🗑️", key=f"d_{idx}"):
        st.session_state.df_membros = st.session_state.df_membros.drop(idx).reset_index(drop=True)
        salvar_dados(st.session_state.df_membros)
        st.rerun()
    st.divider()

# --- BOTÃO FINAL: TODOS NA AGENDA ---
st.markdown("---")
st.subheader("🚀 Configuração Rápida")
st.write("Deseja colocar todos os aniversariantes na sua agenda de uma vez?")
ics_data = gerar_arquivo_ics(df_at)
st.download_button(
    label="📥 Baixar todos para minha Agenda",
    data=ics_data,
    file_name="aniversarios_celula.ics",
    mime="text/calendar",
    use_container_width=True
)