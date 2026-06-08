import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from pathlib import Path

st.set_page_config(
    page_title="Dashboard de Anúncios no AirBnB",
    page_icon="📊",
    layout="wide",
)

st.logo(
    image="https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Airbnb_Logo_B%C3%A9lo.svg/3840px-Airbnb_Logo_B%C3%A9lo.svg.png",
    link="https://www.airbnb.com.br",
    size='large'
)

CAMINHO_ATUAL = Path(__file__).parent

df = pd.read_csv(CAMINHO_ATUAL / 'AirBnBLimpo.csv')

st.sidebar.header("🔍 Filtros")


# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais")

if not df.empty:
    total_host = df['name'].count()
    preco_medio = df['price_cleaned'].mean()
    review_medio = df['number_of_reviews'].mean()
    # ganho_maximo_torneio = df.loc[df_filtrado['Prize_Clean'].idxmax(), "Tournament"]
    # jogo_com_mais_top4 = contagem_por_jogo.idxmax()
    # quantidade = contagem_por_jogo.max()
else:
    total_host, preco_medio, review_medio, _ = 0, 0, 0, "Nenhum dado encontrado"

col1, col2, col3 = st.columns(3)

col1.metric("Total de anúncios", f"{total_host:}")
col2.metric("Preço médio", f"R${preco_medio:,.2f}")
col3.metric("Quantidade média de reviews", f"{review_medio:,.0f}")

graph1, graph2 = st.columns(2)

with graph1:
    if not df.empty:
        df_agrupado = df.groupby(['neighbourhood_cleansed', 'room_type']).size().reset_index(name='Quantidade')
        
        ordem_bairros = df_agrupado.groupby('neighbourhood_cleansed')['Quantidade'].sum().sort_values(ascending=True).index.tolist()
        
        df_agrupado['neighbourhood_cleansed'] = pd.Categorical(
            df_agrupado['neighbourhood_cleansed'], 
            categories=ordem_bairros, 
            ordered=True
        )
        
        df_plot = df_agrupado.sort_values('neighbourhood_cleansed')

        grafico_aluguei_por_bairro = px.bar(
            df_plot,  
            x='Quantidade',
            y='neighbourhood_cleansed',
            orientation='h',
            color='room_type',
            title="Aluguéis por Bairro e tipos de quarto",
            labels={
                'Quantidade': 'Quantidade de Anúncios',  
                'neighbourhood_cleansed': 'Bairro',        
                'room_type': 'Tipo de Quarto'            
            },
            height=1200
        )
        
        grafico_aluguei_por_bairro.update_yaxes(categoryorder='array', categoryarray=ordem_bairros)

        grafico_aluguei_por_bairro.update_layout(
            legend=dict(
                orientation="h",     # Define a orientação como horizontal
                yanchor="bottom",    # Ancorado pela base da legenda
                y=1.02,              # Posiciona logo acima da área do gráfico (1.0 é o limite do topo)
                xanchor="center",    # Ancorado pelo centro horizontal
                x=0.6                # Centralizado no meio do gráfico
            ),
            dragmode=False
        )
        
        
        st.plotly_chart(grafico_aluguei_por_bairro, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico.")

with graph2:
    if not df.empty:

        grafico_review = px.histogram(
            df,
            x='number_of_reviews',
            labels={
                'count': 'Quantidade de Anúncios',  
                'number_of_reviews': 'Número de Reviews',        
                'room_type': 'Tipo de Quarto'            
            },
            )
        grafico_review.update_yaxes(title_text="Quantidade")

        
        grafico_review.update_traces(
            hovertemplate="Faixa de Valor: %{x}<br>Quantidade: %{y}"
        )

        st.plotly_chart(grafico_review, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico.")