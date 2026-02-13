import streamlit as st
import pandas as pd
import datetime

# criação do sidebar para interação do usuário
def criar_sidebar(df_mov_real):
    st.sidebar.title("Filtros")
    saldo_inicial = st.sidebar.number_input("Saldo inicial", value=264_000.00, format="%.2f")
    data_i = st.sidebar.date_input("Data inicial", value=datetime.date(2026, 1, 1), format="DD.MM.YYYY")
    data_o = st.sidebar.date_input("Data final", value=df_mov_real['Data'].max(), format="DD.MM.YYYY", max_value=df_mov_real['Data'].max())

    # validação das datas
    if not data_i or not data_o:
        st.error("Por favor, selecione a data inicial e a data final antes de continuar.")
        st.stop()

    return saldo_inicial, data_i, data_o