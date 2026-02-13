import streamlit as st
import pandas as pd

from data.loader import carregar_arquivo, limpar
from data.transform import filtrar_periodo, criar_calendario, somar_por_data
from ui.sidebar import criar_sidebar
from ui.tabs import (
    aba_visão_geral,
    aba_comparativos,
    aba_fluxo_diario
)

# ---------------------------------------
# CONFIGURAÇÕES
# ---------------------------------------

st.set_page_config(layout="wide", page_title="Análise de Fluxo de Caixa - Golden Age", page_icon="🏙️")

cor_proj = 'silver'
cor_real = "goldenrod"

URL = "https://drive.google.com/uc?export=download&id=1kk39jFbijG9yNKJog5tybL7I842-xelp"

# ---------------------------------------
# CARREGAMENTO E LIMPEZA DOS DADOS
# ---------------------------------------

dfs = carregar_arquivo(URL)
dfs = {k: limpar(v) for k, v in dfs.items()}

df_rct_real = dfs["rct_real"]
df_rct_proj = dfs["rct_proj"]
df_dsp_real = dfs["dsp_real"]
df_dsp_proj = dfs["dsp_proj"]
df_categorias = dfs["categorias"]

# ---------------------------------------
# SIDEBAR
# ---------------------------------------

saldo_inicial, data_i, data_o = criar_sidebar(df_rct_real)

# ---------------------------------------
# MOVIMENTOS FINANCEIROS
# ---------------------------------------

df_mov_real = filtrar_periodo(pd.concat([df_rct_real, df_dsp_real]), data_i, data_o)
df_mov_proj = filtrar_periodo(pd.concat([df_rct_proj, df_dsp_proj]), data_i, data_o)

# ---------------------------------------
# CALENDÁRIO E FLUXO DIÁRIO
# ---------------------------------------

intervalo, df_calendario = criar_calendario(data_i, data_o)

# PROJETADO
proj_receita = somar_por_data(df_mov_proj, intervalo, "Receita")
proj_receita.iloc[0] += saldo_inicial
proj_despesa = somar_por_data(df_mov_proj, intervalo, "Despesa") * -1
saldo_proj = proj_receita + proj_despesa
saldo_proj_acum = saldo_proj.cumsum()

# REAL
real_receita = somar_por_data(df_mov_real, intervalo, "Receita")
real_receita.iloc[0] += saldo_inicial
real_despesa = somar_por_data(df_mov_real, intervalo, "Despesa") * -1
saldo_real = real_receita + real_despesa
saldo_real_acum = saldo_real.cumsum()

df_fluxo = pd.DataFrame({
    "Data": intervalo.date,
    "Receitas Projetadas": proj_receita.values,
    "Despesas Projetadas": proj_despesa.values,
    "Saldo Projetado": saldo_proj_acum.values,
    "Receitas Realizadas": real_receita.values,
    "Despesas Realizadas": real_despesa.values,
    "Saldo Realizado": saldo_real_acum.values,
})

# ---------------------------------------
# INTERFACE — PÁGINAS
# ---------------------------------------

def pagina_visão_geral():
    st.title("Análise de Fluxo de Caixa - Golden Age")
    aba_visão_geral(
        saldo_inicial,
        df_fluxo,
        proj_receita, proj_despesa, saldo_proj_acum,
        real_receita, real_despesa, saldo_real_acum,
        cor_proj, cor_real
    )

def pagina_comparativos():
    st.title("Gráficos Comparativos")
    aba_comparativos(
        df_mov_proj, df_mov_real, df_categorias,
        cor_proj, cor_real
    )

def pagina_fluxo_diario():
    st.header("Fluxo Diário")
    aba_fluxo_diario(df_fluxo)

pages = [
    st.Page(pagina_visão_geral, title="Visão Geral"),
    st.Page(pagina_comparativos, title="Comparativos"),
    st.Page(pagina_fluxo_diario, title="Fluxo Diário"),
]

pg = st.navigation(pages, position="top")
pg.run()