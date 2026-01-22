from playwright.sync_api import sync_playwright
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from product_filter import is_valid_pc_product

def get_magazineluiza_prices(query="RTX 4060", max_pages=2):
    """
    Scraper do Magazine Luiza com suporte a múltiplas páginas.
    
    Args:
        query (str): Termo de busca
        max_pages (int): Número máximo de páginas para scrapar (padrão: 2)
    """
    
    all_products = []
    
    with sync_playwright() as p:
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
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        # Loop para scrapar múltiplas páginas
        for page_num in range(1, max_pages + 1):
            try:
                # URL com paginação
                url = f"https://www.magazineluiza.com.br/busca/{query.replace(' ', '+').lower()}/?page={page_num}"
                print(f"Buscando página {page_num}/{max_pages}: {url}")
                
                time.sleep(2)
                page.goto(url, wait_until="networkidle", timeout=90000)
                
                print(f"  Aguardando carregamento dos produtos...")
                time.sleep(3)
                
                try:
                    page.wait_for_selector('a[data-testid="product-card-container"]', timeout=20000)
                except:
                    print(f"  Timeout aguardando seletores - página {page_num} pode estar vazia")
                    break  # Não há mais páginas

                # Scroll
                page.evaluate("window.scrollTo(0, 1000)")
                time.sleep(1)
                page.evaluate("window.scrollTo(0, 2000)")
                time.sleep(2)

                # Pegar cards
                product_cards = page.locator('a[data-testid="product-card-container"]').all()
                
                if not product_cards:
                    print(f"  Nenhum produto encontrado na página {page_num}")
                    break
                
                print(f"  Encontrados {len(product_cards)} produtos na página {page_num}.")

                for card in product_cards:
                    try:
                        # Título
                        title_locator = card.locator('[data-testid="product-title"]')
                        if not title_locator.count():
                            continue
                        
                        
                        title = title_locator.first.inner_text().strip()
                        
                        # Filtrar produtos não relacionados a PC
                        if not is_valid_pc_product(title):
                            continue

                        # Preço
                        price_locator = card.locator('[data-testid="price-value"]')
                        
                        price_text = "0,00"
                        if price_locator.count():
                            price_text = price_locator.first.inner_text().strip()
                            price_text = price_text.replace("ou ", "").strip()
                        else:
                            continue
                        
                        # Limpeza
                        price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                        price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                        
                        try:
                            price_float = float(price_clean)
                        except ValueError:
                            price_float = 0.0
                        
                        if price_float <= 0:
                            continue

                        # Link
                        item_url = card.get_attribute('href')
                        if item_url and not item_url.startswith('http'):
                            item_url = "https://www.magazineluiza.com.br" + item_url

                        all_products.append({
                            "product_name": title,
                            "price": price_float,
                            "store": "Magazine Luiza",
                            "url": item_url
                        })
                        
                    except Exception as e:
                        continue
                
                # Delay entre páginas (importante para evitar bloqueio)
                if page_num < max_pages:
                    import random
                    delay = random.uniform(4, 7)
                    print(f"  Aguardando {delay:.1f}s antes da próxima página...")
                    time.sleep(delay)
                        
            except Exception as e:
                 print(f"  Erro na página {page_num}: {e}")
                 break
        
        browser.close()

    print(f"Total de produtos coletados (Magazine Luiza): {len(all_products)}")
    return all_products

if __name__ == "__main__":
    data = get_magazineluiza_prices("RTX 4060")
    print("\n--- Dados Extraídos (Magazine Luiza) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
