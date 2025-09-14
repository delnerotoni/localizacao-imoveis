from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

# Configurações
service = Service('./src/msedgedriver.exe')
options = webdriver.EdgeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Edge(service=service, options=options)

os.makedirs('data', exist_ok=True)

url = 'https://www.vivareal.com.br/aluguel/sp/sao-paulo/'
driver.get(url)
time.sleep(3)

# Aceita cookies se aparecer
try:
    aceitar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceitar todos os cookies")]'))
    )
    aceitar.click()
    print("🍪 Cookies aceitos com sucesso.")
    time.sleep(2)
except:
    print("⚠️ Aviso de cookies não encontrado ou já fechado.")

# Scroll lento para garantir carregamento
for i in range(10):
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(1)

# Espera os links dos imóveis aparecerem
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/imovel/")]'))
    )
except:
    print("🚫 Os links dos imóveis não apareceram.")
    driver.quit()
    exit()

# Coleta os links e textos
cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/imovel/")]')

dados = []
for card in cards:
    try:
        link = card.get_attribute('href')
        texto = card.text.strip()

        if texto:  # ignora elementos vazios
            dados.append({
                'Descrição': texto,
                'Link': link
            })
    except Exception as e:
        print(f"⚠️ Erro ao extrair card: {e}")

driver.quit()

df = pd.DataFrame(dados)
if not df.empty:
    df.to_csv('data/imoveis_vivareal.csv', index=False, encoding='utf-8-sig')
    print(f"✅ {len(df)} imóveis coletados e salvos em 'data/imoveis_vivareal.csv'")
else:
    print("🚫 Nenhum imóvel coletado. Verifique o XPath ou a estrutura da página.")










