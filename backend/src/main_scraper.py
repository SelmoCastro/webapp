import json
import time
import random
from scrapers.kabum import get_kabum_prices
from scrapers.pichau import get_pichau_prices
from scrapers.terabyte import get_terabyte_prices
from db import save_price_history

def run_all_scrapers(query="RTX 4060"):
    results = []
    
    print(f"=== Iniciando Scraping Multilojas para '{query}' ===")
    
    # 1. Kabum
    try:
        print("\n[1/3] Executando Kabum...")
        kabum_data = get_kabum_prices(query)
        results.extend(kabum_data)
        print(f"-> {len(kabum_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Kabum: {e}")

    # Delay aleatório (2 a 5 segundos)
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)

    # 2. Pichau
    try:
        print("\n[2/3] Executando Pichau...")
        pichau_data = get_pichau_prices(query)
        results.extend(pichau_data)
        print(f"-> {len(pichau_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Pichau: {e}")

    # Delay aleatório (2 a 5 segundos)
    delay = random.uniform(2, 5)
    print(f"Aguardando {delay:.2f}s...")
    time.sleep(delay)

    # 3. Terabyte
    try:
        print("\n[3/3] Executando Terabyte...")
        terabyte_data = get_terabyte_prices(query)
        results.extend(terabyte_data)
        print(f"-> {len(terabyte_data)} produtos encontrados.")
    except Exception as e:
        print(f"Erro no scraper Terabyte: {e}")

    print(f"\n=== Finalizado. Total de produtos coletados: {len(results)} ===")
    
    # Salvar no Banco de Dados
    if results:
        print("Salvando no Supabase...")
        save_price_history(results)
    
    return results


if __name__ == "__main__":
    data = run_all_scrapers("RTX 4060")
    
    # Opcional: Salvar em arquivo para debug
    with open("dataset_multiloja_poc.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Dados salvos em dataset_multiloja_poc.json")
