import streamlit as st
import pandas as pd
import plotly.express as px
from ui.charts import criar_grafico_fluxo, criar_grafico_comparativo1, criar_grafico_comparativo2

def aba_visão_geral(
        saldo_inicial, 
        df_fluxo, 
        proj_receita, proj_despesa, saldo_proj_acum, 
        real_receita, real_despesa, saldo_real_acum, 
        cor_proj, cor_real
        ):
    st.subheader("Visão Geral")
    c1, c2, c3 = st.columns([1,1,2], border=True, vertical_alignment="top")
    c1.metric("Total de Receitas Projetadas", f"R$ {proj_receita.sum() - saldo_inicial:,.2f}")
    c1.space('medium')
    c1.metric("Total de Despesas Projetadas", f"R$ {proj_despesa.sum():,.2f}")
    c1.space('medium') 
    c1.metric("Menor saldo projetado no período", f"R$ {saldo_proj_acum.min():,.2f}")

    c2.metric("Total de Receitas Realizadas", f"R$ {real_receita.sum() - saldo_inicial:,.2f}", delta=f"R$ {real_receita.sum() - proj_receita.sum():,.2f}", delta_color="normal")
    c2.space('small')
    c2.metric("Total de Despesas Realizadas", f"R$ {real_despesa.sum():,.2f}", delta=f"R$ {real_despesa.sum() - proj_despesa.sum():,.2f}", delta_color="inverse")
    c2.space('small')
    c2.metric("Menor saldo realizado no período", f"R$ {saldo_real_acum.min():,.2f}", delta=f"R$ {saldo_real_acum.min() - saldo_proj_acum.min():,.2f}", delta_color="normal")

    c3.plotly_chart(criar_grafico_fluxo(df_fluxo, cor_proj, cor_real), width='stretch')

def aba_comparativos(df_mov_proj, df_mov_real, df_categorias, cor_proj, cor_real):
    col1, col2 = st.columns(2, border=True, vertical_alignment="bottom")
    tipo = col1.pills(
        "Selecione o tipo de movimento financeiro", ("Receita", "Despesa"),
        selection_mode="single", 
        default="Despesa" 
        )
        
    # gráfico comparativo por Categoria (Projetado x Realizado)
    df_tipo_proj = df_mov_proj[df_mov_proj["Tipo"] == tipo].groupby("Categoria")["Valor"].sum().reset_index()
    df_tipo_real = df_mov_real[df_mov_real["Tipo"] == tipo].groupby("Categoria")["Valor"].sum().reset_index()
    df_tipo_comparativo = df_tipo_proj.merge(df_tipo_real, on="Categoria", how="outer", suffixes=("_proj", "_real")).fillna(0)
    df_tipo_comparativo = df_tipo_comparativo.rename(columns={"Valor_proj": "Projetado", "Valor_real": "Realizado"})

    col1.plotly_chart(criar_grafico_comparativo1(df_tipo_comparativo, tipo, cor_proj, cor_real), width='stretch')



    # gráfico comparativo por Subcategoria dentro de uma Categoria
    df_categorias_filtradas = df_categorias[df_categorias["Tipo"] == tipo]
    padrão = "Pessoal" if tipo == "Despesa" else "Cotas"

    categoria = col2.pills("Selecione a categoria", df_categorias_filtradas["Categoria"].unique(), selection_mode="multi", default=padrão)

    df_categoria_proj = df_mov_proj[(df_mov_proj["Categoria"].isin(categoria)) & (df_mov_proj["Tipo"] == tipo)].groupby(['Subcategoria'])['Valor'].sum().reset_index()
    df_categoria_real = df_mov_real[(df_mov_real["Categoria"].isin(categoria)) & (df_mov_real["Tipo"] == tipo)].groupby(['Subcategoria'])['Valor'].sum().reset_index()

    df_categoria_comparativo = df_categoria_proj.merge(df_categoria_real, on="Subcategoria", how="outer", suffixes=("_proj", "_real")).fillna(0)
    df_categoria_comparativo = df_categoria_comparativo.rename(columns={"Valor_proj": "Projetado", "Valor_real": "Realizado"})

    col2.plotly_chart(criar_grafico_comparativo2(df_categoria_comparativo, tipo, categoria, cor_proj, cor_real), width='stretch')

def aba_fluxo_diario(df_fluxo):
    st.dataframe(
        df_fluxo, 
        width='stretch', 
        height='content', 
        column_config={ "Data": st.column_config.DateColumn(format="DD.MM.YYYY"), 
                        "Receitas Projetadas": st.column_config.NumberColumn(format="accounting"),
                        "Despesas Projetadas": st.column_config.NumberColumn(format="accounting"),
                        "Saldo Projetado": st.column_config.NumberColumn(format="accounting"),
                        "Receitas Realizadas": st.column_config.NumberColumn(format="accounting"),
                        "Despesas Realizadas": st.column_config.NumberColumn(format="accounting"), 
                        "Saldo Realizado": st.column_config.NumberColumn(format="accounting") 
                    })   