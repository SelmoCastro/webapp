import json
import time
import random
from scrapers.kabum import get_kabum_prices
from scrapers.pichau import get_pichau_prices
from scrapers.terabyte import get_terabyte_prices
from scrapers.mercadolivre import get_mercadolivre_prices
from scrapers.amazon import get_amazon_prices
from db import save_price_history

def run_all_scrapers(query="RTX 4060"):
    results = []
    
    print(f"=== Iniciando Scraping Multilojas para '{query}' ===")
    
    # 1. Kabum
    try:
        print("\n[1/5] Executando Kabum...")
        kabum_data = get_kabum_prices(query)
        results.extend(kabum_data)
        print(f"-> {len(kabum_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Kabum: {e}")

    # Delay aleatório
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)

    # 2. Pichau
    try:
        print("\n[2/5] Executando Pichau...")
        pichau_data = get_pichau_prices(query)
        results.extend(pichau_data)
        print(f"-> {len(pichau_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Pichau: {e}")

    # Delay aleatório
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)

    # 3. Terabyte
    try:
        print("\n[3/5] Executando Terabyte...")
        terabyte_data = get_terabyte_prices(query)
        results.extend(terabyte_data)
        print(f"-> {len(terabyte_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Terabyte: {e}")
    
    # Delay aleatório
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)
    
    # 4. Mercado Livre
    try:
        print("\n[4/5] Executando Mercado Livre...")
        ml_data = get_mercadolivre_prices(query)
        results.extend(ml_data)
        print(f"-> {len(ml_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Mercado Livre: {e}")
    
    # Delay aleatório
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)
    
    # 5. Amazon
    try:
        print("\n[5/5] Executando Amazon...")
        amazon_data = get_amazon_prices(query)
        results.extend(amazon_data)
        print(f"-> {len(amazon_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Amazon: {e}")

    print(f"\n=== Finalizado. Total de produtos coletados: {len(results)} ===")
    
    # Salvar no Banco de Dados
    if results:
        print("Salvando no Supabase...")
        save_price_history(results)
    
    return results


if __name__ == "__main__":
    products_to_search = [
        "RTX 4060",
        "RTX 4070",
        "RX 7600",
        "Ryzen 5 5600",
        "Ryzen 7 5700X3D",
        "Core i5 13400F",
        "Memória RAM 16GB DDR4",
        "Memória RAM 16GB DDR5",
        "SSD NVMe 1TB",
        "Fonte 650W"
    ]

    all_results = []
    
    print(f"=== Iniciando Coleta de {len(products_to_search)} Termos ===")

    for product in products_to_search:
        print(f"\n>>> Buscando: {product}")
        results = run_all_scrapers(product)
        all_results.extend(results)
        
        # Delay extra entre produtos para não sobrecarregar
        delay = random.uniform(5, 10)
        print(f"Sleeping {delay:.2f}s before next product...")
        time.sleep(delay)
    
    # Opcional: Salvar em arquivo para debug
    with open("dataset_multiloja_poc.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    print(f"\nColeta Finalizada. Total acumulado: {len(all_results)} itens.")
    print("Dados salvos em dataset_multiloja_poc.json")
