import streamlit as st
import pandas as pd
from utils.template_game import renderizar_pagina_jogo

# 1. Configuração de página única (obrigatória no topo)
st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("liquid_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = carregar_dados()

# Guardamos o df no session_state para a página home.py poder usar sem baixar de novo
st.session_state['df_completo'] = df

# 2. Define a página estática da Home
home_page = st.Page("utils/home.py", title="Visão Geral", icon="🏠")

# Função fábrica para gerar chamadas exclusivas para cada jogo
def criar_funcao_pagina(nome_jogo, dados):
    def pagina_especifica():
        renderizar_pagina_jogo(nome_jogo, dados)
    # Aqui está o truque: mudamos o nome interno da função para o nome do jogo!
    pagina_especifica.__name__ = f"pagina_{nome_jogo.lower().replace(' ', '_')}"
    return pagina_especifica

# 3. Descobre os jogos e cria as páginas dinâmicas sem conflito de URL
jogos_disponiveis = df['Game'].unique()
paginas_jogos = []

for jogo in jogos_disponiveis:
    # Geramos uma função nomeada unicamente para este jogo
    funcao_da_pagina = criar_funcao_pagina(jogo, df)
    
    pagina = st.Page(
        funcao_da_pagina, 
        title=jogo, 
        icon="🎮"
    )
    paginas_jogos.append(pagina)

# 4. Monta o menu da barra lateral organizando por categorias
pg = st.navigation({
    "Principal": [home_page],
    "Modalidades": paginas_jogos
})

# 5. Executa o dashboard
pg.run()