import streamlit as st
import pandas as pd
import plotly.express as px


def renderizar_pagina_jogo(nome_do_jogo, df_completo):
    st.title(f"📊 Análise Detalhada - {nome_do_jogo}")
    
    # 1. Filtra os dados na raiz apenas para o jogo desta página
    df_jogo = df_completo[df_completo['Game'] == nome_do_jogo]
    
    if df_jogo.empty:
        st.warning(f"Nenhum dado encontrado para o jogo {nome_do_jogo}.")
        return

    # 2. Seus filtros comuns (ex: Ano) baseados apenas nesse jogo
    anos_disponiveis = sorted(df_jogo['Date'].dt.year.unique())
    anos_selecionados = st.sidebar.multiselect(
        f"Anos ({nome_do_jogo})", anos_disponiveis, default=anos_disponiveis
    )
    
    df_filtrado = df_jogo[df_jogo['Date'].dt.year.isin(anos_selecionados)]

    # 3. Seus blocos de métricas e gráficos (que agora funcionam para qualquer jogo)
    col1, col2 = st.columns(2)
    
    with col1:
        # Exemplo: Histograma de premiações que você já criou
        if not df_filtrado.empty:
            grafico_hist = px.histogram(
                df_filtrado,
                x='Prize_Clean',
                nbins=50,
                title=f"Distribuição de premiações em {nome_do_jogo}",
                labels={'Prize_Clean': 'Valor (USD)', 'count': 'Quantidade'}
            )
            grafico_hist.update_yaxes(title_text="Quantidade")
            st.plotly_chart(grafico_hist, use_container_width=True)