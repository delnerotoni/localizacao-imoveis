import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Opcional (para o mapa)
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# =========================
# Configuração básica
# =========================
st.set_page_config(page_title="Imóveis SP", layout="wide")
st.title("🏠 Imóveis em São Paulo - VivaReal")

# =========================
# Carregamento de dados (cache)
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv('data/imoveis_vivareal.csv')
    # Em alguns ambientes seu CSV pode usar "Descricao" sem acento — normalize:
    if 'Descrição' not in df.columns and 'Descricao' in df.columns:
        df.rename(columns={'Descricao': 'Descrição'}, inplace=True)
    df.dropna(subset=['Descrição'], inplace=True)
    df.drop_duplicates(inplace=True)
    return df

df = load_data()

# =========================
# Extração de informações
# =========================
re_quartos = re.compile(r'(\d+)\s+quarto[s]?', re.IGNORECASE)
re_banheiros = re.compile(r'(\d+)\s+banheiro[s]?', re.IGNORECASE)
re_area = re.compile(r'(\d{2,4})\s?m²', re.IGNORECASE)
re_preco = re.compile(r'R\$\s?([\d\.\,]+)', re.IGNORECASE)
# Tenta capturar “em Vila Olímpia”, “no Brooklin”, “na Bela Vista”, etc.
re_bairro = re.compile(r'\b(?:em|no|na|nos|nas)\s+([A-Za-zÀ-ÿ\s\-]+?)(?:\s*[-,]|$)', re.IGNORECASE)

def extrair_info(texto: str) -> dict:
    texto = texto or ""
    q = re_quartos.search(texto)
    b = re_banheiros.search(texto)
    a = re_area.search(texto)
    p = re_preco.search(texto)
    bairro_m = re_bairro.search(texto)

    preco = None
    if p:
        preco = int(p.group(1).replace('.', '').replace(',', ''))

    return {
        'Quartos': int(q.group(1)) if q else None,
        'Banheiros': int(b.group(1)) if b else None,
        'Área': int(a.group(1)) if a else None,
        'Preço': preco,
        'Bairro': bairro_m.group(1).strip() if bairro_m else None
    }

info_df = df['Descrição'].fillna('').apply(extrair_info).apply(pd.Series)
df = pd.concat([df, info_df], axis=1)

# =========================
# Sidebar: Filtros
# =========================
st.sidebar.header("Filtros")

min_quartos = int(df['Quartos'].min()) if not df['Quartos'].isna().all() else 1
max_quartos = int(df['Quartos'].max()) if not df['Quartos'].isna().all() else 5
quartos = st.sidebar.slider("Número mínimo de quartos", min_quartos, max_quartos, min_quartos)

min_area = int(df['Área'].min()) if not df['Área'].isna().all() else 10
max_area = int(df['Área'].max()) if not df['Área'].isna().all() else 300
area_min = st.sidebar.slider("Área mínima (m²)", min_area, max_area, min_area)

# Filtro opcional por bairro (só mostra valores não nulos)
bairros_validos = sorted([b for b in df['Bairro'].dropna().unique().tolist() if isinstance(b, str)])[:50]
bairro_sel = st.sidebar.multiselect("Bairro (opcional)", options=bairros_validos)

# Faixa de preço (se houver algum preço extraído)
if df['Preço'].notna().any():
    preco_min = int(df['Preço'].min())
    preco_max = int(df['Preço'].max())
    faixa_preco = st.sidebar.slider("Faixa de preço (R$)", preco_min, preco_max, (preco_min, preco_max))
else:
    faixa_preco = None

# =========================
# Aplicando filtros
# =========================
df_filtrado = df[
    (df['Quartos'].fillna(0) >= quartos) &
    (df['Área'].fillna(0) >= area_min)
]

if bairro_sel:
    df_filtrado = df_filtrado[df_filtrado['Bairro'].isin(bairro_sel)]

if faixa_preco:
    mn, mx = faixa_preco
    df_filtrado = df_filtrado[(df_filtrado['Preço'].fillna(0) >= mn) & (df_filtrado['Preço'].fillna(0) <= mx)]

# =========================
# KPIs
# =========================
colA, colB, colC = st.columns(3)
with colA:
    st.metric("Imóveis encontrados", len(df_filtrado))
with colB:
    media_area = int(df_filtrado['Área'].dropna().mean()) if not df_filtrado['Área'].dropna().empty else 0
    st.metric("Área média (m²)", media_area)
with colC:
    if df_filtrado['Preço'].notna().any():
        media_preco = int(df_filtrado['Preço'].dropna().mean())
        st.metric("Preço médio (R$)", media_preco)
    else:
        st.metric("Preço médio (R$)", "—")

# =========================
# Abas
# =========================
tab1, tab2, tab3 = st.tabs(["📋 Tabela", "📈 Gráficos", "📍 Mapa"])

with tab1:
    st.subheader("🔍 Imóveis filtrados")
    cols_show = ['Descrição', 'Bairro', 'Área', 'Quartos', 'Banheiros', 'Preço', 'Link']
    cols_show = [c for c in cols_show if c in df_filtrado.columns]
    st.dataframe(df_filtrado[cols_show].reset_index(drop=True), use_container_width=True)

    st.download_button(
        "⬇️ Baixar CSV filtrado",
        data=df_filtrado.to_csv(index=False).encode('utf-8-sig'),
        file_name="imoveis_filtrados.csv",
        mime="text/csv"
    )

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df_filtrado, x='Área', nbins=30, title='Distribuição de Área Útil')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        if df_filtrado['Preço'].notna().any():
            figp = px.box(df_filtrado.dropna(subset=['Preço']), y='Preço', title='Distribuição de Preço')
            st.plotly_chart(figp, use_container_width=True)
        else:
            st.info("Sem dados de preço para exibir boxplot.")

    fig2 = px.scatter(
        df_filtrado, x='Área', y='Quartos', color='Banheiros',
        title='Área vs. Quartos (colorido por Banheiros)',
        hover_data=[c for c in ['Descrição', 'Bairro', 'Preço', 'Link'] if c in df_filtrado.columns]
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.caption("Ajuste os filtros para refinar o mapa. Geocodificação por bairro (aproximação).")

    # Geocodificação com cache por bairro
    @st.cache_data
    def geocode_bairros(bairros: list):
        geolocator = Nominatim(user_agent="localizacao_imoveis_sp")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, swallow_exceptions=True)
        cache = {}
        for b in bairros:
            if not b or not isinstance(b, str):
                cache[b] = (None, None)
                continue
            loc = geocode(f"{b}, São Paulo, Brasil")
            if loc:
                cache[b] = (loc.latitude, loc.longitude)
            else:
                cache[b] = (None, None)
        return cache

    # Só tenta geocodificar se houver bairros
    bairros_map = df_filtrado['Bairro'].dropna().unique().tolist()
    if len(bairros_map) == 0:
        st.info("Não há bairros identificados nas descrições após os filtros.")
    else:
        cache_coords = geocode_bairros(bairros_map)
        df_filtrado['Latitude'], df_filtrado['Longitude'] = zip(*df_filtrado['Bairro'].map(cache_coords).apply(lambda x: (x[0], x[1])))

        df_mapa = df_filtrado.dropna(subset=['Latitude', 'Longitude'])
        if df_mapa.empty:
            st.warning("Não foi possível geocodificar os bairros filtrados.")
        else:
            m = folium.Map(location=[-23.5505, -46.6333], zoom_start=12, tiles="CartoDB positron")

            from folium.plugins import MarkerCluster
            cluster = MarkerCluster().add_to(m)

            for _, row in df_mapa.iterrows():
                popup_html = f"""
                    <b>{row.get('Descrição','')}</b><br>
                    Bairro: {row.get('Bairro','—')}<br>
                    Área: {row.get('Área','—')} m²<br>
                    Quartos: {row.get('Quartos','—')} | Banheiros: {row.get('Banheiros','—')}<br>
                    Preço: R$ {row.get('Preço','—')}<br>
                    <a href="{row.get('Link','#')}" target="_blank">Abrir anúncio</a>
                """
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    tooltip=f"{row.get('Bairro','SP')} • {row.get('Área','—')}m² • {row.get('Quartos','—')}q",
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color="blue", icon="home", prefix="fa")
                ).add_to(cluster)

            st_folium(m, use_container_width=True, height=520)

