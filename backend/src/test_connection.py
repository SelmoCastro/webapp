from db import get_supabase_client

def test_connection():
    try:
        print("Tentando criar cliente Supabase...")
        client = get_supabase_client()
        
        if not client:
            print("Falha ao criar cliente.")
            return

        print("Cliente criado. Tentando acessar tabela 'price_history'...")
        # Tenta uma consulta simples. Se a tabela não existir, vai dar erro 404/400.
        # Se a chave for invalida, erro 401.
        response = client.table("price_history").select("id").limit(1).execute()
        
        print(f"Conexão bem sucedida via API! Resposta: {response}")

    except Exception as e:
        print(f"Erro na conexão: {e}")

if __name__ == "__main__":
    test_connection()
