from playwright.sync_api import sync_playwright
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from product_filter import is_valid_pc_product

def get_amazon_prices(query="RTX 4060"):
    
    url = f"https://www.amazon.com.br/s?k={query.replace(' ', '+')}"
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
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent=user_agent_str,
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR',
            extra_http_headers={
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
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
            time.sleep(3)
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            print("Aguardando carregamento dos produtos...")
            time.sleep(4)
            
            try:
                page.wait_for_selector('div.s-result-item.s-asin', timeout=20000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll humanizado
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(1.5)
            page.evaluate("window.scrollTo(0, 2000)")
            time.sleep(2)

            # Pegar todos os cards
            product_cards = page.locator('div.s-result-item.s-asin').all()
            
            print(f"Encontrados {len(product_cards)} produtos.")

            for card in product_cards:
                try:
                    # Título
                    title_locator = card.locator('h2 span')
                    if not title_locator.count():
                        continue
                    
                    title = title_locator.first.inner_text().strip()
                    
                    # Filtrar produtos não relacionados a PC
                    if not is_valid_pc_product(title):
                        continue
                    
                    if not title or len(title) < 5:
                        continue

                    # Preço - Amazon tem span.a-offscreen que é mais confiável
                    price_text = "0,00"
                    
                    # Tentar a-offscreen primeiro (mais limpo)
                    offscreen_locator = card.locator('span.a-offscreen')
                    if offscreen_locator.count():
                        price_text = offscreen_locator.first.inner_text().strip()
                    else:
                        # Fallback: montar de a-price-whole + a-price-fraction
                        whole_locator = card.locator('span.a-price-whole')
                        fraction_locator = card.locator('span.a-price-fraction')
                        
                        if whole_locator.count() and fraction_locator.count():
                            whole = whole_locator.first.inner_text().strip()
                            fraction = fraction_locator.first.inner_text().strip()
                            price_text = f"{whole},{fraction}"
                        else:
                            continue
                    
                    # Limpeza do preço "R$ 3.399,00" -> 3399.00
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    # Validar preço
                    if price_float <= 0:
                        continue

                    # Link
                    link_locator = card.locator('h2 a')
                    item_url = None
                    if link_locator.count():
                        href = link_locator.first.get_attribute('href')
                        if href:
                            if href.startswith('http'):
                                item_url = href  # Manter URL completa
                            else:
                                item_url = "https://www.amazon.com.br" + href  # Manter query params

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Amazon",
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
    data = get_amazon_prices("RTX 4060")
    print("\n--- Dados Extraídos (Amazon) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
