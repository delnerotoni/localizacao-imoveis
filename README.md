# 🏠 Localização de Imóveis - VivaReal

![Capa do Projeto](https://copilot.microsoft.com/th/id/BCO.e5916c59-1df5-43e6-a4c0-aadc85741396.png)

Dashboard interativo para explorar imóveis em São Paulo com dados públicos da plataforma VivaReal. Desenvolvido com técnicas de **web scraping**, visualização com **Streamlit**, e preparado para expansão com **Folium** e **Geopy** para geolocalização.

## 🌐 Acesse o App Online

🔗 [Abrir o dashboard no Streamlit Cloud](https://share.streamlit.io/delnerotoni/localizacao-imoveis/src/app.py)

---

## 🚀 Tecnologias Utilizadas

- 🕷️ Web Scraping com Selenium
- 📊 Streamlit para interface interativa
- 📈 Plotly para gráficos dinâmicos
- 📍 Folium + Geopy para mapa interativo
- 🧠 Pandas + Regex para extração de dados estruturados

---

## ✨ Funcionalidades

- 🔎 Filtros interativos por número de quartos, área mínima, bairro e faixa de preço
- 📋 Tabela com detalhes e links diretos para os anúncios
- 📈 Gráficos de distribuição de área e dispersão entre área × quartos
- 📍 Mapa interativo com localização aproximada por bairro
- 📁 Exportação dos imóveis filtrados em CSV
- 📊 KPIs com contagem de imóveis, área média e preço médio
---

## 📂 Estrutura do Projeto

- 📁 `data/` → Dados coletados via scraping  
  └── 🗃️ `imoveis_vivareal.csv`

- 📁 `src/` → Código principal do projeto  
  ├── 🧠 `app.py` → Dashboard Streamlit  
  ├── 🕷️ `coleta.py` → Scraping com Selenium  
  └── 🧩 `msedgedriver.exe` → WebDriver para automação

- 📁 `notebooks/` → Análises exploratórias  
  └── 📓 `exploracao.ipynb`

- 📁 `img/` → vizualização do dash: demo.mp4 
  

- 📄 `requirements.txt` → Dependências do projeto  
- 📄 `README.md` → Documentação

---

## 🛠️ Futuras Implementações

🔄 Botão para atualizar os dados via coleta.py direto do app
🏷️ Filtro por tipo de imóvel (casa, apartamento, comercial)
📱 Versão mobile responsiva
🧠 Modelos preditivos de preço
🌐 Deploy online com Streamlit Cloud

---

## 📄 Licença

Projeto pessoal para fins educacionais. Dados públicos extraídos da plataforma VivaReal.

---

## 🤝 Autor

**Tony Delnero**  
Desenvolvedor de soluções em dados e automação  
GitHub: [@delnerotoni](https://github.com/delnerotoni)

---

## ▶️ Como Rodar Localmente

```bash
git clone https://github.com/delnerotoni/localizacao-imoveis.git
cd localizacao-imoveis
pip install -r requirements.txt
streamlit run src/app.py
```
