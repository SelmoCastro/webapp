from playwright.sync_api import sync_playwright
import json
import time

from fake_useragent import UserAgent

def get_kabum_prices(query="RTX 4060"):
    
    url = f"https://www.kabum.com.br/busca?q={query}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        # Usar um User-Agent Desktop Fixo e Moderno para garantir o layout correto
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page(user_agent=user_agent_str)
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for product cards to appear
            print("Aguardando carregamento dos produtos...")
            try:
                page.wait_for_selector('article.productCard', timeout=15000)
            except:
                print("Timeout aguardando seletores de produto. Verifique se a página carregou corretamente ou se há CAPTCHA.")
                # Snapshot para debug se falhar
                # page.screenshot(path="debug_kabum_fail.png")

            # Get all product cards
            product_cards = page.locator('article.productCard').all()
            print(f"Encontrados {len(product_cards)} cartões de produto.")

            for card in product_cards:
                try:
                    # Title
                    # Tenta seletor padrão ou fallback
                    title_locator = card.locator('.nameCard')
                    if not title_locator.count():
                        title_locator = card.locator('span[class*="nameCard"]')
                    
                    title = title_locator.first.inner_text().strip() if title_locator.count() else "Produto Desconhecido"

                    # Price
                    # Procura pelo preço à vista (geralmente .priceCard)
                    price_locator = card.locator('.priceCard')
                    if not price_locator.count():
                        price_locator = card.locator('span[class*="priceCard"]')
                    
                    price_text = "0,00"
                    if price_locator.count():
                         price_text = price_locator.first.inner_text().strip()
                    
                    # Limpeza do preço
                    price_clean = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    # Manter apenas digitos e ponto
                    price_clean = "".join(c for c in price_clean if c.isdigit() or c == '.')
                    
                    try:
                        price_float = float(price_clean)
                    except ValueError:
                        price_float = 0.0

                    # Link
                    link_locator = card.locator('a.productLink')
                    item_url = None
                    if link_locator.count():
                        href = link_locator.first.get_attribute('href')
                        if href:
                            item_url = "https://www.kabum.com.br" + href

                    products.append({
                        "product_name": title,
                        "price": price_float,
                        "store": "Kabum",
                        "url": item_url
                    })
                    
                except Exception as e:
                    print(f"Erro ao processar um cartão: {e}")
                    continue
                    
        except Exception as e:
             print(f"Erro geral no Playwright: {e}")
        finally:
            browser.close()

    return products

if __name__ == "__main__":
    data = get_kabum_prices("RTX 4060")
    print("\n--- Dados Extraídos (Playwright) ---")
    print(json.dumps(data, indent=4, ensure_ascii=False))
