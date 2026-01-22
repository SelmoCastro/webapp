from playwright.sync_api import sync_playwright
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from product_filter import is_valid_pc_product

def get_mercadolivre_prices(query="RTX 4060"):
    
    url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        # User-Agent Desktop
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent=user_agent_str,
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR'
        )
        
        # Esconder webdriver
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        try:
            # Delays humanizados
            time.sleep(2)
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            print("Aguardando carregamento dos produtos...")
            time.sleep(3)
            
            try:
                page.wait_for_selector('.ui-search-layout__item', timeout=20000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll humanizado
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 1600)")
            time.sleep(2)

            # Pegar todos os cards
            product_cards = page.locator('.ui-search-layout__item').all()
            
            print(f"Encontrados {len(product_cards)} produtos.")

            for card in product_cards:
                try:
                    # Título
                    title_locator = card.locator('.poly-component__title')
                    if not title_locator.count():
                        continue
                    
                    title = title_locator.first.inner_text().strip()
                    
                    # Filtrar produtos não relacionados a PC
                    if not is_valid_pc_product(title):
                        continue

                    # Preço atual (Mercado Livre usa .poly-price__current)
                    price_locator = card.locator('.poly-price__current .andes-money-amount__fraction')
                    
                    price_text = "0"
                    if price_locator.count():
                        price_text = price_locator.first.inner_text().strip()
                    else:
                        # Fallback para seletor genérico
                        price_locator = card.locator('.andes-money-amount__fraction')
                        if price_locator.count():
                            price_text = price_locator.first.inner_text().strip()
                        else:
                            continue
                    
                    # Limpeza do preço "4.396" -> 4396.00
                    # Mercado Livre usa ponto como separador de milhar
                    price_clean = price_text.replace(".", "").replace(",", ".").strip()
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    # Validar preço
                    if price_float <= 0:
                        continue

                    # Link
                    link_locator = card.locator('a.poly-component__title')
                    item_url = None
                    if link_locator.count():
                        href = link_locator.first.get_attribute('href')
                        if href:
                            # Mercado Livre já retorna URL completa
                            item_url = href.split('?')[0]  # Remove tracking params

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Mercado Livre",
                        "url": item_url
                    })
                    
                except Exception as e:
                    # print(f"Erro ao processar um cartão: {e}")
                    continue
                    
        except Exception as e:
             print(f"Erro geral no Playwright: {e}")
        finally:
            browser.close()

    return products

if __name__ == "__main__":
    data = get_mercadolivre_prices("RTX 4060")
    print("\n--- Dados Extraídos (Mercado Livre) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
