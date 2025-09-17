import streamlit as st
import pandas as pd
import re
from datetime import datetime
from pathlib import Path
import io

st.set_page_config(page_title="Imóveis SP", layout="wide")
st.title("🏠 Imóveis em São Paulo - VivaReal")
st.success("✅ App carregado com sucesso")

CSV_PATH = "data/imoveis_vivareal.csv"
CSV_BRUTO = "data/imoveis_bruto.csv"

try:
    from coleta import run_scraper
except Exception as e:
    run_scraper = None
    st.sidebar.warning(f"Scraper não encontrado: {e}")

with st.sidebar:
    st.header("Dados")
    if run_scraper:
        if st.button("🔄 Atualizar dados agora"):
            with st.status("Atualizando dados…", expanded=True) as status:
                try:
                    result = run_scraper(output_path=CSV_PATH, headless=False)
                    status.update(label="Dados atualizados com sucesso", state="complete")
                    st.success(f"{result['registros']} registros coletados.")
                except Exception as e:
                    status.update(label="Erro na coleta", state="error")
                    st.error(str(e))

if not Path(CSV_PATH).exists():
    st.error("❌ CSV não encontrado. Clique em 'Atualizar dados agora'.")
    st.stop()

df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
st.caption(f"📁 Total de imóveis no CSV: {len(df)} — Última modificação: {datetime.fromtimestamp(Path(CSV_PATH).stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}")
st.dataframe(df.head(10))

if df.empty:
    st.warning("⚠️ O CSV está vazio. Tente atualizar os dados.")
    st.stop()

# Regex para extrair dados
re_area = re.compile(r"(\d{2,4})\s?m²", re.IGNORECASE)
re_preco = re.compile(r"R\$\s?([\d\.\,]+)", re.IGNORECASE)
re_bairro = re.compile(r"\b(?:em|no|na|nos|nas)\s+([A-Za-zÀ-ÿ\s\-]+?)(?:\s*[-,]|$)", re.IGNORECASE)
re_bairro_alt = re.compile(r"(.+?),\s+São Paulo", re.IGNORECASE)

def extrair_info(texto):
    texto = re.sub(r"\s+", " ", (texto or "")).strip()
    a = re_area.search(texto)
    p = re_preco.search(texto)
    b = re_bairro.search(texto) or re_bairro_alt.search(texto)
    return {
        "Área": int(a.group(1)) if a else None,
        "Preço": int(p.group(1).replace(".", "").replace(",", "")) if p else None,
        "Bairro": b.group(1).strip() if b else None
    }

df_info = df["Descrição"].apply(extrair_info).apply(pd.Series)
df = pd.concat([df, df_info], axis=1)

st.sidebar.header("Filtros")
quartos = st.sidebar.slider("Quartos mínimos", 0, 5, 0)
area_min = st.sidebar.slider("Área mínima (m²)", 10, 300, 10)
bairros = sorted(set(df["Bairro"].dropna()))
bairro_sel = st.sidebar.multiselect("Bairros", bairros)

if df["Preço"].dropna().size > 0:
    p_min, p_max = int(df["Preço"].min()), int(df["Preço"].max())
    faixa_preco = st.sidebar.slider("Faixa de preço (R$)", p_min, p_max, (p_min, p_max))
else:
    faixa_preco = None

df_filtrado = df.copy()
df_filtrado = df_filtrado[df_filtrado["Área"].fillna(0) >= area_min]
df_filtrado = df_filtrado[df_filtrado["Descrição"].str.contains(fr"{quartos}\s+quarto", case=False, na=False)]
if bairro_sel:
    df_filtrado = df_filtrado[df_filtrado["Bairro"].isin(bairro_sel)]
if faixa_preco:
    df_filtrado = df_filtrado[
        (df_filtrado["Preço"].fillna(0) >= faixa_preco[0]) &
        (df_filtrado["Preço"].fillna(0) <= faixa_preco[1])
    ]

if df_filtrado.empty:
    st.warning("⚠️ Nenhum imóvel corresponde aos filtros atuais.")
    if Path(CSV_BRUTO).exists():
        st.info("💡 Dica: compare com o CSV bruto para entender o que foi descartado.")
        df_bruto = pd.read_csv(CSV_BRUTO, encoding="utf-8-sig")
        st.write(f"🔍 Total no CSV bruto: {len(df_bruto)}")
        st.dataframe(df_bruto.head(10))
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Imóveis encontrados", len(df_filtrado))
col2.metric("Área média", f"{df_filtrado['Área'].dropna().mean():.1f} m²")
col3.metric("Preço médio", f"R$ {df_filtrado['Preço'].dropna().mean():,.2f}")

cols_to_show = ["Descrição", "Bairro", "Área", "Preço"]
if "Link" in df_filtrado.columns:
    cols_to_show.append("Link")
st.subheader("📋 Imóveis filtrados")
st.dataframe(df_filtrado[cols_to_show], use_container_width=True)

# Exportar como Excel
df_export = df_filtrado.copy()
df_export["Descrição"] = df_export["Descrição"].str.replace("\n", " ", regex=True)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, index=False, sheet_name='Imóveis')
output.seek(0)

st.download_button(
    label="📥 Baixar como Excel",
    data=output,
    file_name="imoveis_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.subheader("📊 Gráficos")
colA, colB = st.columns(2)
with colA:
    st.bar_chart(df_filtrado["Área"].dropna())
with colB:
    st.bar_chart(df_filtrado["Preço"].dropna())

# Mapa com coordenadas fixas e legenda dinâmica
with st.container():
    st.subheader("📍 Mapa dos imóveis por bairro")
    st.caption(f"🗺️ Exibindo {len(df_filtrado)} imóveis filtrados no mapa")

    try:
        import folium
        from streamlit_folium import st_folium

        bairros_map = {
            "Moema": [-23.6016, -46.6658],
            "Vila Mariana": [-23.5896, -46.6345],
            "Ipiranga": [-23.5859, -46.6108],
            "Pinheiros": [-23.5675, -46.6931],
            "Tatuapé": [-23.5407, -46.5754],
            "Santana": [-23.5015, -46.6250],
            "Bela Vista": [-23.5614, -46.6482],
            "Campo Belo": [-23.6218, -46.6734],
            "Jardins": [-23.5610, -46.6650],
            "Butantã": [-23.5704, -46.7165]
        }

        mapa = folium.Map(location=[-23.55, -46.63], zoom_start=11)

        for _, row in df_filtrado.iterrows():
            bairro = row.get("Bairro", "").split(",")[0].strip()
            if bairro in bairros_map:
                lat, lon = bairros_map[bairro]
                folium.Marker(
                    [lat, lon],
                    popup=row.get("Descrição", "")[:120],
                    tooltip=bairro
                ).add_to(mapa)

        st_folium(mapa, width=900, height=520)

    except Exception as e:
        st.warning(f"Erro ao carregar mapa: {e}")
        st.code("pip install folium streamlit-folium")
