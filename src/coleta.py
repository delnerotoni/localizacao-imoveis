from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
from datetime import datetime

def run_scraper(output_path="data/imoveis_vivareal.csv", headless=False):
    service = Service('./src/msedgedriver.exe')
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')

    driver = webdriver.Edge(service=service, options=options)
    os.makedirs('data', exist_ok=True)

    url = 'https://www.vivareal.com.br/aluguel/sp/sao-paulo/'
    driver.get(url)
    time.sleep(3)

    try:
        aceitar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Aceitar todos os cookies")]'))
        )
        aceitar.click()
        print("🍪 Cookies aceitos com sucesso.")
        time.sleep(2)
    except:
        print("⚠️ Aviso de cookies não encontrado ou já fechado.")

    for i in range(10):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/imovel/")]'))
        )
    except:
        print("🚫 Os links dos imóveis não apareceram.")
        driver.quit()
        return

    cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/imovel/")]')
    dados = []
    for card in cards:
        try:
            link = card.get_attribute('href')
            texto = card.text.strip()
            if texto:
                dados.append({'Descrição': texto, 'Link': link})
                print(f"✔️ {texto[:80]}...")
        except Exception as e:
            print(f"⚠️ Erro ao extrair card: {e}")

    driver.quit()
    df = pd.DataFrame(dados).drop_duplicates(subset="Link")

    if not df.empty:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        df.to_csv("data/imoveis_bruto.csv", index=False, encoding='utf-8-sig')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        df.to_csv(f"data/imoveis_backup_{timestamp}.csv", index=False, encoding='utf-8-sig')
        print(f"✅ {len(df)} imóveis coletados e salvos.")
        return {
            "registros": len(df),
            "arquivo": output_path,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        raise Exception("Nenhum imóvel coletado. Verifique a estrutura da página.")

