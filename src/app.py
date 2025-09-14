import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 🚀 Carrega os dados
df = pd.read_csv('data/imoveis_vivareal.csv')
df.dropna(subset=['Descrição'], inplace=True)
df.drop_duplicates(inplace=True)

# 🔍 Extrai info da descrição
def extrair_info(texto):
    quartos = re.search(r'(\d+)\s+quarto', texto)
    banheiros = re.search(r'(\d+)\s+banheiro', texto)
    area = re.search(r'(\d+)\s?m²', texto)
    return {
        'Quartos': int(quartos.group(1)) if quartos else None,
        'Banheiros': int(banheiros.group(1)) if banheiros else None,
        'Área': int(area.group(1)) if area else None
    }

info_df = df['Descrição'].apply(extrair_info).apply(pd.Series)
df = pd.concat([df, info_df], axis=1)

# 🎯 Título do app
st.set_page_config(page_title="Imóveis SP", layout="wide")
st.title("🏠 Imóveis em São Paulo - VivaReal")

# 🎛️ Filtros interativos
col1, col2 = st.columns(2)
with col1:
    quartos = st.slider("Número mínimo de quartos", 1, 5, 2)
with col2:
    area_min = st.slider("Área mínima (m²)", 10, 300, 50)

df_filtrado = df[(df['Quartos'] >= quartos) & (df['Área'] >= area_min)]

# 📋 Tabela de imóveis
st.subheader(f"🔍 {len(df_filtrado)} imóveis encontrados")
st.dataframe(df_filtrado[['Descrição', 'Área', 'Quartos', 'Banheiros', 'Link']], use_container_width=True)

# 📊 Gráfico de área útil
fig = px.histogram(df_filtrado, x='Área', nbins=30, title='Distribuição de Área Útil')
st.plotly_chart(fig, use_container_width=True)

# 📈 Gráfico de dispersão
fig2 = px.scatter(df_filtrado, x='Área', y='Quartos', color='Banheiros',
                  title='Área vs. Quartos (colorido por Banheiros)',
                  hover_data=['Descrição', 'Link'])
st.plotly_chart(fig2, use_container_width=True)

