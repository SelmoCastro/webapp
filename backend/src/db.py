import os
from supabase import create_client, Client
from dotenv import load_dotenv

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
    """
    supabase = get_supabase_client()
    if not supabase:
        return

    if not data:
        print("Nenhum dado para salvar.")
        return

    try:
        # data deve ser uma lista de dicts com chaves:
        # product_name, price, store, url, category (opcional), installment_price (opcional)
        
        # O Supabase retorna os dados inseridos em 'data' na versão mais recente
        response = supabase.table("price_history").insert(data).execute()
        
        # Verifica se houve inserção (a resposta é um objeto APIResponse)
        # Geralmente se não lançar exceção, funcionou.
        print(f"Sucesso! {len(data)} registros salvos no banco de dados.")
        
    except Exception as e:
        print(f"Erro ao salvar no Supabase: {e}")
