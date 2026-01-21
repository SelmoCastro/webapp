from playwright.sync_api import sync_playwright
import json
import time

def get_americanas_prices(query="RTX 4060"):
    
    url = f"https://www.americanas.com.br/busca/{query.replace(' ', '-').lower()}"
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
            time.sleep(4)  # Americanas usa React, precisa de mais tempo
            
            try:
                page.wait_for_selector('div[data-fs-custom-product-card="true"]', timeout=20000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1.5)
            page.evaluate("window.scrollTo(0, 1600)")
            time.sleep(2)

            # Pegar cards (Americanas usa data-fs-custom-product-card)
            product_cards = page.locator('div[data-fs-custom-product-card="true"]').all()
            
            print(f"Encontrados {len(product_cards)} produtos.")

            for card in product_cards:
                try:
                    # Título
                    title_locator = card.locator('h3[class*="ProductCard_productName"]')
                    if not title_locator.count():
                        continue
                    
                    title = title_locator.first.inner_text().strip()

                    # Preço (discountPrice = preço à vista/PIX)
                    price_locator = card.locator('span[class*="ProductCard_discountPrice"]')
                    
                    price_text = "0,00"
                    if price_locator.count():
                        price_text = price_locator.first.inner_text().strip()
                    else:
                        # Fallback para preço regular
                        price_locator_regular = card.locator('p[class*="ProductCard_productPrice"]')
                        if price_locator_regular.count():
                            price_text = price_locator_regular.first.inner_text().strip()
                        else:
                            continue
                    
                    # Limpeza "R$ 2.099,99" -> 2099.99
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    if price_float <= 0:
                        continue

                    # Link
                    link_locator = card.locator('a')
                    item_url = None
                    if link_locator.count():
                        href = link_locator.first.get_attribute('href')
                        if href:
                            if href.startswith('http'):
                                item_url = href.split('?')[0]
                            else:
                                item_url = "https://www.americanas.com.br" + href.split('?')[0]

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Americanas",
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
    data = get_americanas_prices("RTX 4060")
    print("\n--- Dados Extraídos (Americanas) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
