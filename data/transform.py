import pandas as pd

#filtro do intervalo de tempo definido pelo usuário
def filtrar_periodo(df,data_i,data_o):
    f = (df['Data'].dt.date >= data_i) & (df['Data'].dt.date <= data_o)
    return df[f]


def somar_por_data(df, intervalo, tipo):
    return (
        df[df["Tipo"] == tipo]
        .groupby("Data")["Valor"]
        .sum()
        .reindex(intervalo, fill_value=0)
    )

def criar_calendario(data_i, data_o):
    intervalo = pd.date_range(data_i, data_o, freq="D")
    return intervalo, pd.DataFrame({
        "Data": intervalo,
        "Ano": intervalo.year,
        "Mês": intervalo.month,
        "Dia": intervalo.day,
        "Dia da semana": intervalo.strftime("%a")
        })