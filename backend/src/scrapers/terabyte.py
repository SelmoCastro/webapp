from playwright.sync_api import sync_playwright
import json
import time

from fake_useragent import UserAgent

def get_terabyte_prices(query="RTX 4060"):
    
    url = f"https://www.terabyteshop.com.br/busca?str={query}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        ua = UserAgent()
        user_agent_str = ua.random

        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page(user_agent=user_agent_str)
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            print("Aguardando carregamento dos produtos...")
            try:
                # Seletor baseado na inspeção
                page.wait_for_selector('.product-item', timeout=15000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll to load more items
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(1)

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
