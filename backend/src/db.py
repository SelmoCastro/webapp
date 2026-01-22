import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from product_normalizer import normalize_product_name

# Load env variables from .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    if not url or not key:
        print("ERRO: SUPABASE_URL ou SUPABASE_KEY não configurados no arquivo .env")
        return None
    return create_client(url, key)

def save_price_history(data: list):
    """
    Salva uma lista de dicionários de preços no Supabase.
    Adiciona campo 'normalized_name' para identificação consistente.
    """
    supabase = get_supabase_client()
    if not supabase:
        return

    if not data:
        print("Nenhum dado para salvar.")
        return

    try:
        # Adicionar normalized_name e timestamp a cada item
        enriched_data = []
        for item in data:
            # Normalizar nome do produto
            normalized_name = normalize_product_name(
                item.get('product_name', ''),
                item.get('store')
            )
            
            enriched_item = {
                "product_name": item.get('product_name'),
                "normalized_name": normalized_name,  # NOVO CAMPO
                "price": item.get('price'),
                "store": item.get('store'),
                "url": item.get('url'),
                "timestamp": datetime.now().isoformat()  # Timestamp automático
            }
            enriched_data.append(enriched_item)
        
        # Inserir no Supabase
        response = supabase.table("price_history").insert(enriched_data).execute()
        
        print(f"Sucesso! {len(enriched_data)} registros salvos no banco de dados.")
        
    except Exception as e:
        print(f"Erro ao salvar no Supabase: {e}")
