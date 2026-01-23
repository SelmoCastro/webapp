#!/usr/bin/env python3
"""
Script para importar dados do JSON para o Supabase
"""
import json
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db import save_price_history

def import_json_to_supabase(json_file):
    """Importa dados do JSON para o Supabase"""
    
    print(f"=== Importando {json_file} para Supabase ===\n")
    
    # Ler JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total de produtos no JSON: {len(data)}\n")
    
    # Validar dados
    valid_data = []
    for item in data:
        if item.get('price', 0) > 0 and item.get('product_name'):
            valid_data.append(item)
    
    print(f"Produtos válidos (preço > 0): {len(valid_data)}\n")
    
    # Salvar no Supabase em lotes de 100
    batch_size = 100
    total_saved = 0
    
    for i in range(0, len(valid_data), batch_size):
        batch = valid_data[i:i+batch_size]
        print(f"Salvando lote {i//batch_size + 1} ({len(batch)} produtos)...")
        
        try:
            save_price_history(batch)
            total_saved += len(batch)
        except Exception as e:
            print(f"Erro ao salvar lote: {e}")
            continue
    
    print(f"\n✅ Importação concluída!")
    print(f"Total salvo: {total_saved}/{len(valid_data)} produtos")

if __name__ == "__main__":
    json_file = "dataset_multiloja_poc.json"
    
    if not os.path.exists(json_file):
        print(f"❌ Arquivo {json_file} não encontrado!")
        sys.exit(1)
    
    import_json_to_supabase(json_file)
