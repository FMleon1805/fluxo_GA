import plotly.express as px

a = 400

# gráfico de linha comparativo entre saldo projetado e realizado ao longo do tempo
def criar_grafico_fluxo(df_fluxo, cor_proj, cor_real):
    return px.line(
        df_fluxo,
        x="Data",
        y=["Saldo Projetado", "Saldo Realizado"],
        labels={"value": "Saldo", "Data": "Data", "variable": "Legenda"},
        color_discrete_map={"Saldo Projetado": cor_proj, "Saldo Realizado": cor_real}
    )

# gráfico comparativo por Categoria (Projetado x Realizado)
def criar_grafico_comparativo1(df, tipo, cor_proj, cor_real):
    return px.bar(
        df,
        y="Categoria",
        x=["Projetado", "Realizado"],
        title=f"{tipo}s por Categoria",
        labels={"value": "Valor", "Categoria": "Categoria", "variable": "Legenda"},
        color_discrete_map={"Projetado": cor_proj, "Realizado": cor_real},
        barmode="group",
        orientation="h",
        text_auto=True,
        height= a
    )

# gráfico comparativo por Subcategoria dentro de uma Categoria
def criar_grafico_comparativo2(df, tipo, categoria, cor_proj, cor_real):
    return px.bar(
        df,
        y="Subcategoria",
        x=["Projetado", "Realizado"],
        title=f"{tipo}s com {', '.join(categoria)}",
        labels={"value": "Valor", "Subcategoria": "Subcategoria", "variable": "Legenda"},
        color_discrete_map={"Projetado": cor_proj, "Realizado": cor_real},
        barmode="group",
        orientation="h",
        text_auto=True,
        height= a
    )