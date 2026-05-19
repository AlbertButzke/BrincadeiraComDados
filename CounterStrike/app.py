import streamlit as st

# 1. Configuração que vale para todas as páginas (deve ser a primeira linha do app.py)
st.set_page_config(layout="wide")

# 2. Define os caminhos e títulos das páginas usando st.Page
home_page = st.Page("paginas/home.py", title="Visão Geral", icon="🏠")
dota2 = st.Page("paginas/Dota2.py", title="Análise Dota2", icon="📈")

# 3. Cria a navegação na barra lateral automaticamente
pg = st.navigation([home_page, dota2])

# 4. Executa a página selecionada pelo usuário
pg.run()