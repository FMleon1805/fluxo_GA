import streamlit as st
import datetime
import pandas as pd
import plotly.express as px

altura = 600

cor_proj = 'silver'
cor_real = "goldenrod"

st.set_page_config(layout="wide")

print(f"Pandas: {pd.__version__}")
print(f"Streamlit: {st.__version__}")

caminho = "https://drive.google.com/uc?export=download&id=1kk39jFbijG9yNKJog5tybL7I842-xelp"

arquivo = pd.ExcelFile(caminho)

df_rct_real = pd.read_excel(arquivo, "rct_real")
df_rct_proj = pd.read_excel(arquivo, "rct_proj")
df_dsp_real = pd.read_excel(arquivo, "dsp_real")
df_dsp_proj = pd.read_excel(arquivo, "dsp_proj")
df_categorias = pd.read_excel(arquivo, "categorias")

# ajeita os cabeçalhos e converte os tipos de dados
def limpar(df):
    df.columns = df.iloc[1]
    df = df.drop(index=range(0,2)).reset_index(drop=True)
    if 'Valor' in df.columns: df['Valor'] = df['Valor'].astype(float)
    if 'Data' in df.columns: df['Data'] = pd.to_datetime(df['Data'], format="%d/%m/%Y")
    return df

df_rct_real = limpar(df_rct_real)
df_rct_proj = limpar(df_rct_proj)
df_dsp_real = limpar(df_dsp_real)
df_dsp_proj = limpar(df_dsp_proj)
df_categorias = limpar(df_categorias)


#criação de dfs derivados 'movimentos financeiros'

df_mov_proj = pd.concat([df_rct_proj, df_dsp_proj])
df_mov_real = pd.concat([df_rct_real, df_dsp_real])

# criação do sidebar para interação do usuário
st.sidebar.header("Filtros")
saldo_inicial = st.sidebar.number_input("Saldo inicial", value=264_000.00, format="%.2f", step=None)
data_i = st.sidebar.date_input("Data inicial", value=datetime.date(2026, 1, 1), format="DD.MM.YYYY")
data_o = st.sidebar.date_input("Data final", value=df_mov_real['Data'].max(), format="DD.MM.YYYY")

# validação das datas
if not data_i or not data_o:
    st.error("Por favor, selecione a data inicial e a data final antes de continuar.")
    st.stop()

#filtro dos movimentos financeiros com base na interação do usuário
def filtro(df,data_i,data_o):
    f = (df['Data'].dt.date >= data_i) * (df['Data'].dt.date <= data_o)
    return df[f]

df_mov_real = filtro(df_mov_real,data_i,data_o)
df_mov_proj = filtro(df_mov_proj,data_i,data_o)

#criação da tabela derivada 'calendário'

intervalo =pd.date_range(data_i, data_o, freq="D")
df_calendário = pd.DataFrame({
    "Data": intervalo,
    "Ano": intervalo.year,
    "Mês": intervalo.month,
    "Dia": intervalo.day,
    "Dia da semana": intervalo.strftime("%a")})

#criação da tabela derivada 'fluxo diário'

def somar_por_data(df, intervalo, tipo):
    return (
        df[df["Tipo"] == tipo]
        .groupby("Data")["Valor"]
        .sum()
        .reindex(intervalo, fill_value=0)
    )

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

# Interface com abas para organizar as visualizações

st.title("Análise de Fluxo de Caixa - Golden Age")

tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Comparativos", "Fluxo Diário", "Cenários"])

with tab1:
    c1, c2, c3 = st.columns([1,1,2])
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

    # gráfico de linha comparativo entre saldo projetado e realizado ao longo do tempo
    fig_fluxo = px.line(
        df_fluxo,
        x="Data",
        y=["Saldo Projetado", "Saldo Realizado"],
        labels={"value": "Saldo", "Data": "Data", "variable": "Legenda"},
        color_discrete_map={"Saldo Projetado": cor_proj, "Saldo Realizado": cor_real}
    )

    c3.plotly_chart(fig_fluxo, use_container_width=True)


with tab2:
    t2_col1, t2_col2, t2_col3 = st.columns(3)

    t2_col1.space('medium')
    tipo = t2_col1.pills("Selecione o tipo de movimento financeiro", ("Receita", "Despesa"), selection_mode="single", default="Despesa")
    t2_col1.space('medium')
    # gráfico comparativo por Categoria (Projetado x Realizado)
    df_tipo_proj = df_mov_proj[df_mov_proj["Tipo"] == tipo].groupby("Categoria")["Valor"].sum().reset_index()
    df_tipo_real = df_mov_real[df_mov_real["Tipo"] == tipo].groupby("Categoria")["Valor"].sum().reset_index()
    df_tipo_comparativo = df_tipo_proj.merge(df_tipo_real, on="Categoria", how="outer", suffixes=("_proj", "_real")).fillna(0)
    df_tipo_comparativo = df_tipo_comparativo.rename(columns={"Valor_proj": "Projetado", "Valor_real": "Realizado"})

    fig_tipo_comparativo = px.bar(
        df_tipo_comparativo,
        y="Categoria",
        x=["Projetado", "Realizado"],
        title=f"{tipo}s por Categoria",
        labels={"value": "Valor", "Categoria": "Categoria", "variable": "Legenda"},
        color_discrete_map={"Projetado": cor_proj, "Realizado": cor_real},
        barmode="group",
        orientation="h",
        text_auto=True,
        height=altura
    )

    t2_col2.plotly_chart(fig_tipo_comparativo, use_container_width=True)

    # gráfico comparativo por Subcategoria dentro de uma Categoria
    df_categorias_filtradas = df_categorias[df_categorias["Tipo"] == tipo]
    padrão = "Pessoal" if tipo == "Despesa" else "Cotas"
    categoria = t2_col1.pills("Selecione a categoria", df_categorias_filtradas["Categoria"].unique(), selection_mode="multi", default=padrão)

    df_categoria_proj = df_mov_proj[(df_mov_proj["Categoria"].isin(categoria)) & (df_mov_proj["Tipo"] == tipo)].groupby(['Subcategoria'])['Valor'].sum().reset_index()
    df_categoria_real = df_mov_real[(df_mov_real["Categoria"].isin(categoria)) & (df_mov_real["Tipo"] == tipo)].groupby(['Subcategoria'])['Valor'].sum().reset_index()

    df_categoria_comparativo = df_categoria_proj.merge(df_categoria_real, on="Subcategoria", how="outer", suffixes=("_proj", "_real")).fillna(0)
    #df_categoria_comparativo = df_categoria_comparativo[(df_categoria_comparativo["Valor_proj"] != 0) & (df_categoria_comparativo["Valor_real"] != 0)]
    df_categoria_comparativo = df_categoria_comparativo.rename(columns={"Valor_proj": "Projetado", "Valor_real": "Realizado"})

    fig_categoria_comparativo = px.bar(
        df_categoria_comparativo,
        y="Subcategoria",
        x=["Projetado", "Realizado"],
        title=f"{tipo}s com {', '.join(categoria)}",
        labels={"value": "Valor", "Subcategoria": "Subcategoria", "variable": "Legenda"},
        color_discrete_map={"Projetado": cor_proj, "Realizado": cor_real},
        barmode="group",
        orientation="h",
        text_auto=True,
        height=altura
    )

    t2_col3.plotly_chart(fig_categoria_comparativo, use_container_width=True)

with tab3:
    st.dataframe(
        df_fluxo,
        width='stretch',
        height='content',
        column_config={
            "Data": st.column_config.DateColumn(format="DD.MM.YYYY"),
            "Receitas Projetadas": st.column_config.NumberColumn(format="accounting"),
            "Despesas Projetadas": st.column_config.NumberColumn(format="accounting"),
            "Saldo Projetado": st.column_config.NumberColumn(format="accounting"),
            "Receitas Realizadas": st.column_config.NumberColumn(format="accounting"),
            "Despesas Realizadas": st.column_config.NumberColumn(format="accounting"),
            "Saldo Realizado": st.column_config.NumberColumn(format="accounting")
        }
    )

# criação de um ambiente de projeção de cenários para o usuário, 
# onde ele pode filtrar as categorias de despesa em uma cópia de df_dsp_proj e ainda inserir novas despesas projetadas em um novo df_usuário.
# df_usuário será estruturado em ['Data','Descrição', 'Valor mensal','Parcelas']
# a combinação desse filtro + df_usuário gerará um gráfico de linha comparativo entre o saldo projetado original e o saldo projetado com o cenário,
# para que o usuário possa avaliar o impacto de suas decisões financeiras.

colunas = {"Data", "Descrição", "Valor mensal", "Parcelas"}
df_usuario = tab4.data_editor(
    pd.DataFrame([colunas]),
    num_rows='fixed'
)





