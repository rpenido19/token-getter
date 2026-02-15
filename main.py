import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

# Lista de fichas que você quer cruzar
TOKENS = [
    "Beast",
    "Treasure",
]

def setup_driver():
    """Configura o driver do Chrome"""
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    return uc.Chrome(options=options)

def click_load_more(driver):
    """Clica no botão 'Carregar mais cartas' até não estar mais disponível"""
    while True:
        try:
            botao = driver.find_element(By.CSS_SELECTOR, '#exibir_mais_cards > input')
            if botao.is_displayed() and botao.is_enabled():
                driver.execute_script("arguments[0].click();", botao)
                time.sleep(2)  # Reduzi para 2 segundos
            else:
                break
        except:
            break

def extract_card_names(html_content):
    """Extrai nomes de cartas do HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    nomes_cartas = []
    
    selectors = '#mtg-cards .mtg-linhas .mtg-name a, #mtg-cards .mtg-linhas .mtg-name-aux a'
    
    for div in soup.select(selectors):
        nome = div.text.strip()
        
        if '//' not in nome:
            continue
        
        lados = [lado.strip().lower() for lado in nome.split('//')]
        if len(lados) != 2:
            continue
        
        lado_esq, lado_dir = lados
        
        # Verificar combinações de tokens
        for token1 in TOKENS:
            if token1.lower() in lado_esq:
                for token2 in TOKENS:
                    if token2 != token1 and token2.lower() in lado_dir:
                        nomes_cartas.append(nome)
                        break
                break
    
    return nomes_cartas

def get_card_names(driver, token):
    """Busca cartas que criam tokens específicos"""
    url = f"https://www.ligamagic.com.br/?view=cards%2Fsearch&card={token}&tipo=1"
    driver.get(url)
    time.sleep(5)  # Tempo de espera reduzido
    
    click_load_more(driver)
    time.sleep(2)  # Aguarda carregamento final
    
    return extract_card_names(driver.page_source)

def main():
    """Função principal"""
    driver = setup_driver()
    
    try:
        # Acessa a página inicial para estabelecer sessão
        driver.get("https://www.ligamagic.com.br")
        time.sleep(3)
        
        resultado = set()
        tokens_usados = set()
        
        for ficha in TOKENS:
            print(f"🔍 Buscando por: {ficha}")
            cartas = get_card_names(driver, ficha)
            
            for carta in cartas:
                resultado.add(carta)
                # Marca os tokens presentes na ficha encontrada
                for token in TOKENS:
                    if token.lower() in carta.lower():
                        tokens_usados.add(token)
            
            time.sleep(1)  # Delay entre buscas
        
        # Salva resultados
        if resultado:
            with open("fichas_encontradas.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(sorted(resultado)))
            print(f"✅ Encontradas {len(resultado)} fichas")
        else:
            print("❌ Nenhuma ficha encontrada")
        
        tokens_nao_encontrados = sorted(set(TOKENS) - tokens_usados)
        if tokens_nao_encontrados:
            with open("fichas_nao_encontradas.txt", "w", encoding="utf-8") as f:
                f.write('\n'.join(tokens_nao_encontrados))
            print(f"❗ {len(tokens_nao_encontrados)} fichas não encontradas")
        
        print("✅ Busca concluída!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()