from playwright.sync_api import sync_playwright
import json
import time

def get_magazineluiza_prices(query="RTX 4060"):
    
    url = f"https://www.magazineluiza.com.br/busca/{query.replace(' ', '+').lower()}/"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
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
        
        try:
            time.sleep(2)
            page.goto(url, wait_until="networkidle", timeout=90000)
            
            print("Aguardando carregamento dos produtos...")
            time.sleep(3)
            
            try:
                page.wait_for_selector('a[data-testid="product-card-container"]', timeout=20000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 2000)")
            time.sleep(2)

            # Pegar cards (Magazine Luiza usa data-testid)
            product_cards = page.locator('a[data-testid="product-card-container"]').all()
            
            print(f"Encontrados {len(product_cards)} produtos.")

            for card in product_cards:
                try:
                    # Título
                    title_locator = card.locator('[data-testid="product-title"]')
                    if not title_locator.count():
                        continue
                    
                    title = title_locator.first.inner_text().strip()

                    # Preço (data-testid="price-value")
                    price_locator = card.locator('[data-testid="price-value"]')
                    
                    price_text = "0,00"
                    if price_locator.count():
                        price_text = price_locator.first.inner_text().strip()
                        # Remove "ou " que aparece antes do preço PIX
                        price_text = price_text.replace("ou ", "").strip()
                    else:
                        continue
                    
                    # Limpeza "R$ 4.129,90" -> 4129.90
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    if price_float <= 0:
                        continue

                    # Link (o próprio card é um link)
                    item_url = card.get_attribute('href')
                    if item_url and not item_url.startswith('http'):
                        item_url = "https://www.magazineluiza.com.br" + item_url

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Magazine Luiza",
                        "url": item_url
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
             print(f"Erro geral no Playwright: {e}")
        finally:
            browser.close()

    return products

if __name__ == "__main__":
    data = get_magazineluiza_prices("RTX 4060")
    print("\n--- Dados Extraídos (Magazine Luiza) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
