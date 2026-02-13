import pandas as pd

def carregar_arquivo(url):
    arquivo = pd.ExcelFile(url) 
    return { 
        "rct_real": pd.read_excel(arquivo, "rct_real"), 
        "rct_proj": pd.read_excel(arquivo, "rct_proj"), 
        "dsp_real": pd.read_excel(arquivo, "dsp_real"), 
        "dsp_proj": pd.read_excel(arquivo, "dsp_proj"), 
        "categorias": pd.read_excel(arquivo, "categorias"), 
    }

# ajeita os cabeçalhos e converte os tipos de dados
def limpar(df):
    df.columns = df.iloc[1]
    df = df.drop(index=range(0,2)).reset_index(drop=True)
    if 'Valor' in df.columns: df['Valor'] = df['Valor'].astype(float)
    if 'Data' in df.columns: df['Data'] = pd.to_datetime(df['Data'], format="%d/%m/%Y")
    return df