import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Ganhos da Team Liquid no CS, DotA, LoL e R6",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
url = "https://raw.githubusercontent.com/AlbertButzke/BrincadeiraComDados/main/CounterStrike/liquid_data.csv"
df = pd.read_csv(url, index_col=0)

df.to_csv("liquid_data.csv", index=False)  # Salva uma cópia local dos dados

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].dt.date
anos_disponiveis = sorted(df['Date'].dt.year.unique()) #sorted para organizar os anos em ordem crescente
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis) #multiselect permite selecionar múltiplas opções

# Filtro de Jogo
jogos_disponiveis = sorted(df['Game'].unique())
jogos_selecionadas = st.sidebar.multiselect("Jogo", jogos_disponiveis, default=jogos_disponiveis)

# Filtro por Classificação
df['Place_Int'] = df['Place'].str.extract('(\d+)').astype(float)
min_pos = int(df['Place_Int'].min())
max_pos = int(df['Place_Int'].max())
alcance_colocacao = st.sidebar.slider(
    "Filtrar por Colocação (Ex: 1º ao 10º)",
    min_value=min_pos,
    max_value=max_pos,
    value=(min_pos, max_pos) # Valor inicial (todo o alcance)
)
df_filtrado = df[
    (df['Place_Int'] >= alcance_colocacao[0]) & 
    (df['Place_Int'] <= alcance_colocacao[1])
]

# Filtro por valor de premiação
# min_premiacao = float(df['Prize_Clean'].min())
# max_premiacao = float(df['Prize_Clean'].max())
# alcance_premiacao = st.sidebar.slider(
#     "Filtrar por Valor de Premiação",
#     min_value=min_premiacao,
#     max_value=max_premiacao,
#     value=(min_premiacao, max_premiacao) # Valor inicial (todo o alcance)
# )
# df_filtrado = df[
#     (df['Prize_Clean'] >= alcance_premiacao[0]) & 
#     (df['Prize_Clean'] <= alcance_premiacao[1])
# ]
marcos = [0, 500, 1000, 5000, 10000, 50000, 100000, 250000, 500000, 1000000, 2000000, float(df['Prize_Clean'].max())]
faixa_selecionada = st.sidebar.select_slider(
    "Selecione a Faixa de Premiação",
    options=marcos,
    value=(0, float(df['Prize_Clean'].max())),  # Valor inicial (do mínimo ao máximo)
    format_func=lambda x: f"US$ {x:,}" if x >= 1000 else f"US$ {x}"
)
df_filtrado = df[
    (df['Prize_Clean'] >= faixa_selecionada[0]) & 
    (df['Prize_Clean'] <= faixa_selecionada[1])
]
st.sidebar.info(f"Torneios encontrados: {len(df_filtrado)}")

# Filtro por Tier
# tier_disponiveis = sorted(df['Tier'].unique())
# tier_selecionados = st.sidebar.multiselect("Tier", tier_disponiveis, default=tier_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['Date'].dt.year.isin(anos_selecionados)) &
    (df['Game'].isin(jogos_selecionadas)) &
    # (df['Place'].isin(classificacao_selecionados))
    (df['Place_Int'] >= alcance_colocacao[0]) & 
    (df['Place_Int'] <= alcance_colocacao[1]) 
    # (df['Tier'].isin(tier_selecionados))
    # (df['Place_Int'] >= alcance_premiacao[0]) & 
    # (df['Place_Int'] <= alcance_premiacao[1]) 
]
df_filtrado = df_filtrado.drop(columns=['Prize'])

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Ganhos da Team Liquid no CS, DotA, LoL e R6")
st.markdown("Explore os dados de ganhos de torneios em cada Jogo do time da Team Liquid. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais")

pattern_top4 = r'(?<!\d)(1st|2nd|3rd|4th)'
df_top4 = df_filtrado[df_filtrado['Place'].str.contains(pattern_top4, na=False)]
contagem_por_jogo = df_top4['Game'].value_counts()

if not df_filtrado.empty:
    ganho_medio = df_filtrado['Place'].mode()[0]
    ganho_maximo = df_filtrado['Prize_Clean'].max()
    ganho_maximo_torneio = df_filtrado.loc[df_filtrado['Prize_Clean'].idxmax(), "Tournament"]
    jogo_com_mais_top4 = contagem_por_jogo.idxmax()
    quantidade = contagem_por_jogo.max()
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, "Nenhum dado encontrado"

col1, col2 = st.columns(2)
col1.metric("Maior Freqência de Colocação", f"{ganho_medio}")
col2.metric("Quantidade de pódios", f"{quantidade}")

col3, col4, col5 = st.columns(3)
col3.metric("Torneio com a maior premiação", f"{ganho_maximo_torneio:}")
col4.metric("O jogo com mais colocações no Top 4", f"{jogo_com_mais_top4}")
col5.metric("Premiação máxima", f"${ganho_maximo:,.0f}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_premiacoes = df_filtrado.nlargest(10,'Prize_Clean').sort_values('Prize_Clean', ascending=True).reset_index()
        grafico_premiacoes = px.bar(
            top_premiacoes,
            x='Prize_Clean',
            y='Tournament',
            orientation='h',
            title="Top 10 premiações",
            labels={'Prize_Clean': 'Valor da premiação (USD)', 'Tournament': 'Torneio'}
        )
        grafico_premiacoes.update_layout(title_x=0.5, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_premiacoes, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='Prize_Clean',
            nbins=50,
            title="Distribuição de premiações de todos os jogos",
            labels={'Prize_Clean': 'Valor da premiação(USD)', 'count': 'Contagem'}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3 = st.columns(1)

with col_graf3[0]:
    if not df_filtrado.empty:
        jogo_ganho_max = df_filtrado.groupby('Game')['Cumulative_Prize'].max().reset_index()
        jogo_ganho_max = jogo_ganho_max.sort_values(by='Cumulative_Prize', ascending=False)
        grafico_remoto = px.pie(
            jogo_ganho_max,
            names='Jogo',
            values='Ganhos Totais',
            title='Proporção dos ganhos totais',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label', pull=[0.05, 0, 0, 0])
        grafico_remoto.update_layout(title_x=0.5)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")
        
# with col_graf4:
#     if not df_filtrado.empty:
#         df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
#         media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
#         grafico_paises = px.choropleth(media_ds_pais,
#             locations='residencia_iso3',
#             color='usd',
#             color_continuous_scale='rdylgn',
#             title='Salário médio de Cientista de Dados por país',
#             labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
#         grafico_paises.update_layout(title_x=0.1)
#         st.plotly_chart(grafico_paises, use_container_width=True)
#     else:
#         st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")

cols = list(df_filtrado.columns)
# Remove as colunas das posições atuais
cols.remove('Place')
cols.remove('Place_Int')
cols.remove('Tier')
cols.remove('Cumulative_Prize')

cols.insert(2, 'Place_Int')
cols.insert(len(cols), 'Place')


df_filtrado = df_filtrado[cols]

df_filtrado = df_filtrado.rename(columns={
    'Place': 'Colocação Original',
    'Place_Int': 'Posição Numérica',
    'Prize_Clean': 'Premiação (USD)',
    'Date': 'Data',
    'Tournamente': 'Torneio',
    'Result': 'Resultado'
})

st.dataframe(df_filtrado)