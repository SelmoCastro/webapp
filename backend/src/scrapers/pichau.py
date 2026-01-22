from playwright.sync_api import sync_playwright
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from product_filter import is_valid_pc_product

from fake_useragent import UserAgent

def get_pichau_prices(query="RTX 4060"):
    
    url = f"https://www.pichau.com.br/search?q={query}"
    print(f"Buscando {url} com Playwright...")
    
    products = []
    
    with sync_playwright() as p:
        # Usar um User-Agent Desktop Fixo e Moderno
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

        # Launch browser com mais argumentos anti-detecção
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
            
            # Usar domcontentloaded ao invés de networkidle (mais rápido)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as goto_err:
                print(f"Erro no page.goto (tentando load): {goto_err}")
                page.goto(url, wait_until="load", timeout=60000)
            
            print("Aguardando carregamento dos produtos...")
            time.sleep(5)  # Aumentado para 5s
            
            # Aguardar seletores com mais tolerância
            try:
                page.wait_for_selector('a[class*="MuiGrid-item"], div[class*="MuiGrid-item"], article', timeout=15000)
            except:
                print("Timeout aguardando seletores de produto.")
                # Não retornar, continuar tentando

            # Scroll mais humanizado
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1)
            page.evaluate("window.scrollTo(0, 1600)")

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
                    
                    # Filtrar produtos não relacionados a PC
                    if not is_valid_pc_product(title):
                        continue

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
