from playwright.sync_api import sync_playwright
import json
import time

def get_pichau_prices(query="RTX 4060"):
    
    url = f"https://www.pichau.com.br/search?q={query}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        # Use a common user agent
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for products
            print("Aguardando carregamento dos produtos...")
            try:
                # Wait based on inspection: main grid items usually have a specific pattern or just wait for 'h2' which is title
                page.wait_for_selector('div[class*="MuiGrid-item"]', timeout=15000)
            except:
                print("Timeout aguardando seletores de produto.")

            # Scroll to load more items if lazy loading
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(1)

            # Get all product link containers which are the cards
            # Based on inspection: a[href*="/"] inside main 
            # But let's be more specific to avoid header/footer links
            # The grid items have class MuiGrid-item. Inside them there is an <a> tag.
            product_cards = page.locator('div[class*="MuiGrid-item"] a[href*="/"]').all()
            
            # Filter out non-product links if any (usually sidebar banners might be tricky, but checking for price element helps)
            
            print(f"Encontrados {len(product_cards)} potenciais produtos.")

            for card in product_cards:
                try:
                    # Title (h2)
                    title_locator = card.locator('h2')
                    if not title_locator.count():
                        continue # Not a product card
                    
                    title = title_locator.first.inner_text().strip()

                    # Price (div[class*="price_vista"])
                    price_locator = card.locator('div[class*="price_vista"]')
                    
                    price_text = "0,00"
                    if price_locator.count():
                         price_text = price_locator.first.inner_text().strip()
                    else:
                        # Fallback: check for any R$ text if specific class fails
                        # but keep it simple first
                        continue 
                    
                    # Limpeza do preço "R$ 2.499,99 à vista" -> 2499.99
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    # Manter apenas digitos e ponto
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0
                    
                    if price_float == 0.0:
                        continue


                    # Link
                    href = card.get_attribute('href')
                    item_url = None
                    if href:
                        if href.startswith("http"):
                            item_url = href
                        else:
                            item_url = "https://www.pichau.com.br" + href

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Pichau",
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
    data = get_pichau_prices("RTX 4060")
    print("\n--- Dados Extraídos (Pichau) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
