from playwright.sync_api import sync_playwright
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from product_filter import is_valid_pc_product

def get_terabyte_prices(query="RTX 4060"):
    
    url = f"https://www.terabyteshop.com.br/busca?str={query}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        # Usar um User-Agent Desktop Fixo e Moderno
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent=user_agent_str,
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR'
        )
        
        # Injetar script para esconder webdriver
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        try:
            # Delays humanizados
            time.sleep(3)
            
            # Usar domcontentloaded para evitar timeout
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as goto_err:
                print(f"Erro no page.goto (tentando load): {goto_err}")
                page.goto(url, wait_until="load", timeout=60000)
            
            print("Aguardando carregamento dos produtos...")
            time.sleep(5)
            
            # Aguardar com mais tolerância
            try:
                page.wait_for_selector('div.commerce_columns_item_inner', timeout=15000)
            except:
                print("Timeout aguardando seletores de produto.")
                # Continuar tentando

            # Scroll mais humanizado
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 1600)")
            time.sleep(2)

            # Get all product cards
            product_cards = page.locator('.product-item').all()
            
            print(f"Encontrados {len(product_cards)} produtos.")

            for card in product_cards:
                try:
                    # Title
                    title_locator = card.locator('.product-item__name h2')
                    if not title_locator.count():
                        continue 
                    
                    title = title_locator.first.inner_text().strip()
                    
                    # Filtrar produtos não relacionados a PC
                    if not is_valid_pc_product(title):
                        continue

                    # Price (div.prod-new-price span OR .product-item__new-price span)
                    price_locator = card.locator('.prod-new-price span')
                    if not price_locator.count():
                         price_locator = card.locator('.product-item__new-price span')

                    price_text = "0,00"
                    
                    if price_locator.count():
                         # Filter visible ones
                         for i in range(price_locator.count()):
                             txt = price_locator.nth(i).inner_text().strip()
                             if "R$" in txt:
                                 price_text = txt
                                 break
                    else:
                        continue 
                    
                    # Limpeza do preço "R$ 6.614,73" -> 6614.73
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    if price_float == 0.0:
                        continue

                    # Link
                    # The link is usually on the name container or image
                    link_locator = card.locator('a.product-item__name')
                    item_url = None
                    if link_locator.count():
                        href = link_locator.first.get_attribute('href')
                        if href:
                            item_url = href # Terabyte hrefs are usually absolute? Let's check.
                            if not item_url.startswith("http"):
                                item_url = "https://www.terabyteshop.com.br" + item_url

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Terabyte",
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
    data = get_terabyte_prices("RTX 4060")
    print("\n--- Dados Extraídos (Terabyte) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
