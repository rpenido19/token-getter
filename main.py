from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Lista de fichas que você quer cruzar
tokens = [
    "Beast 3/3",
    "Bird 2/2",
    "Elephant 3/3",
    "Treasure",
]

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_card_names(token):
    url = f"https://www.ligamagic.com.br/?view=cards%2Fsearch&card={token}&tipo=1"
    driver.get(url)
    time.sleep(2)

    while True:
        try:
            botao = driver.find_element(By.CSS_SELECTOR, '#exibir_mais_cards > input')
            if botao.is_displayed() and botao.is_enabled():
                driver.execute_script("arguments[0].click();", botao)
                time.sleep(1.5)
            else:
                break
        except:
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    nomes_cartas = []

    for div in soup.select('#mtg-cards .mtg-linhas .mtg-name a, #mtg-cards .mtg-linhas .mtg-name-aux a'):
        nome = div.text.strip()
        nome_lower = nome.lower()

        if '//' not in nome:
            continue

        lados = [lado.strip().lower() for lado in nome.split('//')]
        if len(lados) != 2:
            continue

        lado_esq, lado_dir = lados

        for token1 in tokens:
            if token1.lower() in lado_esq:
                for token2 in tokens:
                    if token2 != token1 and token2.lower() in lado_dir:
                        nomes_cartas.append(nome)
                        break
                break

    return nomes_cartas

# Coleta resultados
resultado = set()
tokens_usados = set()

for ficha in tokens:
    print(f"🔍 Buscando por: {ficha}")
    cartas = get_card_names(ficha)
    for carta in cartas:
        resultado.add(carta)
        # Marca os tokens presentes na ficha encontrada
        for token in tokens:
            if token.lower() in carta.lower():
                tokens_usados.add(token)

# Salva as fichas encontradas
with open("fichas_encontradas.txt", "w", encoding="utf-8") as f:
    for nome in sorted(resultado):
        f.write(nome + "\n")

# Salva as fichas não encontradas
tokens_nao_encontrados = sorted(set(tokens) - tokens_usados)
with open("fichas_nao_encontradas.txt", "w", encoding="utf-8") as f:
    for token in tokens_nao_encontrados:
        f.write(token + "\n")

driver.quit()
print("✅ Busca concluída!")
print("✔️ Resultados salvos em: fichas_encontradas.txt")
print("❗ Fichas não encontradas salvas em: fichas_nao_encontradas.txt")
