import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

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
anos_disponiveis = sorted(df['Date'].dt.year.unique()) #sorted para organizar os anos em ordem crescente
anos_selecionados = st.sidebar.pills("Ano", anos_disponiveis, default=anos_disponiveis, selection_mode="multi") #multiselect permite selecionar múltiplas opções

# Filtro de Jogo
jogos_disponiveis = sorted(df['Game'].unique())
jogos_selecionadas = st.sidebar.pills("Jogo", jogos_disponiveis, default=jogos_disponiveis, selection_mode="multi")

# Filtro por Classificação
df['Place_Int'] = df['Place'].str.extract('(\d+)').astype(float)
df_com_numeros = df.dropna(subset=['Place_Int'])

if not df_com_numeros.empty:
    min_pos = int(df_com_numeros['Place_Int'].min())
    max_pos = int(df_com_numeros['Place_Int'].max())
else:
    min_pos = 1
    max_pos = 10
alcance_colocacao = st.sidebar.slider(
    "Filtrar por Colocação (Ex: 1º ao 10º)",
    min_value=min_pos,
    max_value=max_pos,
    value=(min_pos, max_pos) # Valor inicial (todo o alcance)
)

marcos = [0, 500, 1000, 5000, 10000, 50000, 100000, 250000, 500000, 1000000, 2000000]
max_premio = float(df['Prize_Clean'].max())
if max_premio > marcos[-1]: marcos.append(max_premio)
marcos = sorted(list(set(marcos)))

faixa_selecionada = st.sidebar.select_slider(
    "Selecione a Faixa de Premiação",
    options=marcos,
    value=(marcos[0], marcos[-1]),  # Valor inicial (do mínimo ao máximo)
    format_func=lambda x: f"US$ {int(x):,}".replace(",", ".")
)


# Filtro por Tier
ordem_tiers = ["S-Tier", "A-Tier", "Tier 1", "B-Tier", "Tier 2", "C-Tier", "Tier 3", "D-Tier", "Qualifer", "Monthly", "Weekly"]
tiers_existentes = df['Tier'].unique()
tier_disponiveis = [t for t in ordem_tiers if t in tiers_existentes]
tier_disponiveis += [t for t in tiers_existentes if t not in ordem_tiers]

tier_selecionados = st.sidebar.pills("Tier", 
                                     tier_disponiveis, 
                                     default=tier_disponiveis, 
                                     selection_mode="multi")

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
condicao_colocacao = (
    ((df['Place_Int'] >= alcance_colocacao[0]) & (df['Place_Int'] <= alcance_colocacao[1])) | 
    (df['Place_Int'].isna())
)
df_filtrado = df[
    (df['Date'].dt.year.isin(anos_selecionados)) &
    (df['Game'].isin(jogos_selecionadas)) &
    condicao_colocacao &
    (df['Prize_Clean'] >= faixa_selecionada[0]) & 
    (df['Prize_Clean'] <= faixa_selecionada[1]) &
    (df['Tier'].isin(tier_selecionados))
].copy()
df_filtrado = df_filtrado.sort_values('Date').reset_index(drop=True)
df_filtrado = df_filtrado.drop(columns=['Prize'])
st.sidebar.info(f"Torneios encontrados: {len(df_filtrado)}")

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
col1.metric("Maior Frequência de Colocação", f"{ganho_medio}")
col2.metric("Quantidade de pódios", f"{quantidade}")

col3, col4, col5 = st.columns(3)
col3.metric("Torneio com a maior premiação", f"{ganho_maximo_torneio:}")
col4.metric("O jogo com mais colocações no Top 4", f"{jogo_com_mais_top4}")
col5.metric("Premiação máxima", f"${ganho_maximo:,.0f}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")
df_filtrado = df_filtrado[df_filtrado['Date'].dt.year.isin(anos_selecionados)].copy()
with st.container():
    if not df_filtrado.empty:
        # Criamos uma cópia e ordenamos por data
        df_grafico = df_filtrado.sort_values(by="Date").copy()

        df_grafico['Prize_Clean'] = pd.to_numeric(df_grafico['Prize_Clean'], errors='coerce').fillna(0)
        
        df_grafico['Cumulative_Prize'] = df_grafico.groupby('Game')['Prize_Clean'].cumsum()

        df_grafico['original_index'] = df_grafico.index 

        grafico_acumulativos = px.line(
            df_grafico,
            x='Date',
            y="Cumulative_Prize",
            color='Game',
            markers=True,
            title="Evolução dos Ganhos Acumulados por Jogo",
            custom_data=['Tournament', 'Game', 'Tournament_Link', 'original_index', 'Cumulative_Prize'],
            color_discrete_sequence=px.colors.qualitative.Safe,
            labels={'Cumulative_Prize': 'Premiação Acumulada ($)', 'Date': 'Data'}
        )
        
        grafico_acumulativos.update_traces(
            mode="markers+lines",
            hovertemplate=(
                "<b>Jogo:</b> %{customdata[1]}<br>"
                "<b>Torneio:</b> %{customdata[0]}<br>"
                "<b>Data:</b> %{x|%d/%m/%Y}<br>"
                "<b>Total Acumulado:</b> %{customdata[4]:$,.2f}<br><br>"
                "<i>💡 Clique no ponto para ver os detalhes abaixo</i><extra></extra>" 
            )
        )
        
        ano_min = min(anos_selecionados)
        ano_max = max(anos_selecionados)
        grafico_acumulativos.update_xaxes(
            type='date',
            range=[f"{ano_min}-01-01", f"{ano_max}-12-31"],
            dtick="M12",
            tickformat="%Y",
            showgrid=False,
            showline=True,
            linewidth=1.5,
            linecolor='black',
            tickangle=0
        )
        grafico_acumulativos.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=50, b=40),
            xaxis_title="",
            yaxis_title="",
            hovermode="closest",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text="")
        )
        grafico_acumulativos.update_yaxes(showgrid=True, gridcolor='lightgray', showline=True, linewidth=1.5, linecolor='black')

        # Captura os cliques nos pontos do gráfico
        click_select = plotly_events(grafico_acumulativos, click_event=True, select_event=False, override_height=450)

        # 🌟 MONITORAMENTO INTELIGENTE DE CLIQUE COMPATÍVEL
        # Se o usuário clicar, guardamos as informações em um container de destaque
        ponto_focado = None
        
        if click_select:
            ponto_clicado = click_select[0]
            ponto_index = ponto_clicado['pointNumber']
            curve_index = ponto_clicado['curveNumber']
            
            jogo_da_curva = grafico_acumulativos.data[curve_index].name
            df_filtrado_jogo = df_grafico[df_grafico['Game'] == jogo_da_curva]
            
            if ponto_index < len(df_filtrado_jogo):
                ponto_focado = df_filtrado_jogo.iloc[ponto_index]

        # Se houver um ponto clicado, exibe um painel de destaque lindíssimo antes da tabela
        if ponto_focado is not None:
            st.info(f"🔍 **Resultado focado pelo Gráfico:** {ponto_focado['Tournament']} ({ponto_focado['Game']})")
            
            # Cria colunas de métricas rápidas sobre o ponto clicado
            met_col1, met_col2, met_col3 = st.columns(3)
            with met_col1:
                st.metric("🏅 Colocação", str(ponto_focado['Place']))
            with met_col2:
                st.metric("💰 Premiação Individual", f"US$ {ponto_focado['Prize_Clean']:,.0f}")
            with met_col3:
                if ponto_focado['Tournament_Link']:
                    st.link_button("Abrir Liquipedia ↗️", ponto_focado['Tournament_Link'], use_container_width=True)

    else:
        st.warning("Nenhum dado para exibir no gráfico de ganhos acumulativos.")

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
            nbins=75,
            color = 'Game',
            title="Distribuição de premiações de todos os jogos",
            labels={'Prize_Clean': 'Valor da premiação(USD)', 'Game': 'Jogo', 'count' : 'Quantidade'},
            range_x=[0, df_filtrado['Prize_Clean'].max()]
        )
        grafico_hist.update_yaxes(title_text="Quantidade")
        grafico_hist.update_layout(title_x=0.1)
        grafico_hist.update_traces(
            hovertemplate="Faixa de Valor: %{x}<br>Quantidade: %{y}"
        )
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
            names='Game',
            values='Cumulative_Prize',
            title='Proporção dos ganhos totais',
            hole=0.5,
            labels={
                'Game': 'Jogo', 
                'Cumulative_Prize': 'Premiação Máxima Acumulada'
            }
        )
        grafico_remoto.update_traces(textinfo='percent+label', pull=[0.05, 0, 0, 0])
        grafico_remoto.update_layout(title_x=0.4)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")


st.title("🏅 Pódios da Team Liquid no CS, DotA, LoL e R6")
df_filtrado = df_filtrado[df_filtrado['Date'].dt.year.isin(anos_selecionados)].copy()
if not df_filtrado.empty:
    # Garante que temos uma coluna de Ano para o eixo X
    df_filtrado['Year'] = df_filtrado['Date'].dt.year
    
    cor_map = {'1': '#FFD700', '2': '#C0C0C0', '3': '#CD7F32'}
    labels_map = {'1': '1º Lugar', '2': '2º Lugar', '3': '3º Lugar'}

    df_podios_geral = df_filtrado[df_filtrado['Place_Int'].isin([1, 2, 3])]
    
    if not df_podios_geral.empty:
        max_por_barra = df_podios_geral.groupby(['Year', 'Game', 'Place_Int']).size()
        max_y_global = int(max_por_barra.max()) + 0.5
    else:
        max_y_global = 4.5

    # 2. Função para criar o gráfico Plotly
    def criar_grafico_interativo(df_interno, jogo, titulo, lista_anos):
        df_game = df_interno[(df_interno['Game'] == jogo) & (df_interno['Place_Int'] <= 3)].copy()
        
        if df_game.empty:
            df_counts = pd.DataFrame(columns=['Year', 'Podium', 'Quantidade'])
        
        else:
            # Agrupamos os dados para o Plotly contar as ocorrências
            df_counts = df_game.groupby(['Year', 'Place_Int']).size().reset_index(name='Quantidade')
            df_counts['Podium'] = df_counts['Place_Int'].astype(int).astype(str)

            fig = px.bar(
                df_counts, 
                x='Year', 
                y='Quantidade', 
                color='Podium',
                title=titulo,
                color_discrete_map=cor_map,
                barmode='group', # Colunas lado a lado por ano
                category_orders={"Podium": ['1', '2', '3']}, # Força a ordem da legenda
                labels={
                    'Year': 'Ano'
                }
            )

            fig.update_xaxes(
                type='category',
                categoryorder='array',
                categoryarray= lista_anos,
                # tickvals=lista_anos,
                range=[-0.5, len(lista_anos) - 0.5],
                showgrid=False, 
                showline=True, 
                linewidth=1.5, 
                linecolor='black', 
                tickangle=0
            )
            fig.for_each_trace(lambda t: t.update(
                                                name = labels_map.get(t.name, t.name)
                                                ))

            # Ajustes de layout para ficar limpo no Streamlit
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)', # Fundo 100% transparente
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="center", 
                    x=0.5,
                    title_text="" # Remove a palavra "Place_Str" da legenda
                ),
                font=dict(color='black') # Texto preto nítido
            )
            
            intervalo_ticks = 1 if max_y_global <= 10 else 2

            fig.update_yaxes(
                showgrid=False, 
                showline=True, 
                linewidth=1.5, 
                linecolor='black',
                range=[0, max_y_global],       # <--- Força todos os gráficos a usarem o mesmo teto numérico
                dtick=intervalo_ticks,         # <--- Garante que os passos sejam sempre inteiros (1, 2, 3...) eliminando decimais
                tickformat="d"                 # <--- Força a formatação de exibição estritamente como número Inteiro
            )
            
            return fig

    # 3. Exibição em Grid
    col_a, col_b = st.columns(2)
    col_c, col_d = st.columns(2)

    config = [
        ("Counter-Strike", "Counter-Strike", col_a),
        ("Dota 2", "Dota 2", col_b),
        ("League of Legends", "League of Legends", col_c),
        ("Rainbow Six", "Rainbow Six Siege", col_d)
    ]

    for game_id, nome, col in config:
        with col:
            figura = criar_grafico_interativo(df_filtrado, game_id, nome, sorted(anos_selecionados))
            if figura:
                st.plotly_chart(figura, use_container_width=True)
            else:
                st.info(f"Sem pódios para {game_id}")

else:
    st.warning("O DataFrame filtrado está vazio.")
     
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

df_filtrado_render = df_filtrado.copy()

df_filtrado_render['Tournament'] = df_filtrado_render['Tournament'].fillna('Torneio Desconhecido')
df_filtrado_render['Tournament_Link'] = df_filtrado_render['Tournament_Link'].fillna('')

df_filtrado_render['Tournament_Combined'] = (
    df_filtrado_render['Tournament'] + "#" + df_filtrado_render['Tournament_Link']
)



configuracao_colunas = {
    "Game": st.column_config.TextColumn("💻 Jogo", alignment="left"),
    "Place_Int": st.column_config.NumberColumn("🔢 Posição (Nº)", format="%d", alignment="center"),
    "Place": st.column_config.TextColumn("🏅 Colocação", alignment="center"),
    "Date": st.column_config.DateColumn("📅 Data", format="DD/MM/YYYY", alignment="center"),
    "Prize_Clean": st.column_config.NumberColumn("💰 Premiação (US$)", format="%,.0f", alignment="center"),
    "Result": st.column_config.TextColumn("⚔️ Placar Final", alignment="center"),
    "Tournament_Combined": st.column_config.LinkColumn(
        "🏆 Torneio", 
        alignment="center",
        display_text=r"^([^#]+)"
    ),
    "Tier": st.column_config.TextColumn("📊 Tier ", alignment="center")
}


st.dataframe(
    df_filtrado_render,
    hide_index=True,
    use_container_width=True,
    
    column_order=['Date', 'Game', 'Tournament_Combined', 'Place_Int', 'Tier', 'Place', 'Prize_Clean', 'Result'],
    
    column_config=configuracao_colunas
)