# 🏠 Localização de Imóveis - VivaReal

![Capa do Projeto](https://copilot.microsoft.com/th/id/BCO.e5916c59-1df5-43e6-a4c0-aadc85741396.png)

Dashboard interativo para explorar imóveis em São Paulo com dados públicos da plataforma VivaReal. Desenvolvido com técnicas de **web scraping**, visualização com **Streamlit**, e preparado para expansão com **Folium** e **Geopy** para geolocalização.

---

## 🚀 Tecnologias Utilizadas

- 🕷️ **Web Scraping** com Selenium  
- 📊 **Streamlit** para interface interativa  
- 📈 **Plotly** para gráficos dinâmicos  
- 📍 **Folium + Geopy** *(em breve)* para mapa interativo  

---

## ✨ Funcionalidades

- 🔎 Filtro por número de quartos e área mínima  
- 🏷️ Filtro por tipo de imóvel (casa, apartamento, comercial)  
- 📋 Tabela com detalhes e links diretos  
- 📈 Gráficos de distribuição e dispersão  
- 📁 Exportação dos imóveis filtrados em CSV  
- 🗺️ *(Futuro)* Mapa interativo com localização dos imóveis  

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

- 📁 `img/` → Imagens do projeto  
  └── 🖼️ `estrutura.png`

- 📄 `requirements.txt` → Dependências do projeto  
- 📄 `README.md` → Documentação

---

## 🛠️ Futuras Implementações

- 📍 Mapa interativo com **Folium**  
- 🌐 Geolocalização com **Geopy**  
- 📱 Versão mobile responsiva  
- 🧠 Modelos preditivos de preço  

---

## 📄 Licença

Projeto pessoal para fins educacionais. Dados públicos extraídos da plataforma VivaReal.

---

## 🤝 Autor

**Tony Delnero**  
Desenvolvedor de soluções em dados e automação  
GitHub: [@delnerotoni](https://github.com/delnerotoni)

---

## ▶️ Como Rodar

```bash
pip install -r requirements.txt
streamlit run src/app.py
