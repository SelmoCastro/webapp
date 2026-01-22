"""
Sistema de Normalização de Nomes de Produtos

Identifica produtos equivalentes mesmo com nomes diferentes entre lojas.
Exemplo: "RTX 4060 ASUS 8GB" e "ASUS Dual RTX4060 8GB GDDR6" são reconhecidos como o mesmo produto.
"""

import re
from unidecode import unidecode

# Marcas conhecidas por categoria
KNOWN_BRANDS = {
    'gpu': ['nvidia', 'amd', 'asus', 'msi', 'gigabyte', 'evga', 'zotac', 'palit', 'gainward', 'pny', 'galax', 'colorful'],
    'cpu': ['intel', 'amd'],
    'ram': ['kingston', 'corsair', 'gskill', 'g.skill', 'hyperx', 'crucial', 'patriot', 'team group', 'adata'],
    'motherboard': ['asus', 'msi', 'gigabyte', 'asrock', 'biostar'],
    'storage': ['samsung', 'western digital', 'wd', 'seagate', 'kingston', 'crucial', 'sandisk'],
    'psu': ['corsair', 'evga', 'seasonic', 'thermaltake', 'cooler master', 'xpg'],
}

# Padrões regex para modelos
GPU_PATTERN = r'(?:rtx|gtx|rx|radeon)\s*(\d{4})\s*(ti|super|xt|xe)?'
CPU_AMD_PATTERN = r'ryzen\s*(\d+)\s*(\d{4}\w*)'
CPU_INTEL_PATTERN = r'(?:core\s*i|i)(\d+)\s*(\d{5}\w*)'
RAM_CAPACITY_PATTERN = r'(\d+)\s*gb(?:\s*ddr(\d))?'
STORAGE_CAPACITY_PATTERN = r'(\d+)\s*(gb|tb)'

# Stopwords para remover
STOPWORDS = [
    'placa', 'de', 'video', 'vídeo', 'processador', 'memória', 'memoria',
    'kit', 'pc', 'gamer', 'computer', 'desktop', 'para', 'com', 'sem',
    'dual', 'oc', 'edition', 'black', 'white', 'rgb', 'led'
]

def extract_features(product_name):
    """
    Extrai características principais do produto.
    
    Args:
        product_name (str): Nome completo do produto
        
    Returns:
        dict: {
            'brand': str,
            'model': str,
            'variant': str,
            'capacity': str,
            'category': str
        }
    """
    name = product_name.lower()
    name = unidecode(name)  # Remove acentos
    
    features = {
        'brand': None,
        'model': None,
        'variant': None,
        'capacity': None,
        'category': None
    }
    
    # Detectar categoria e marca
    for category, brands in KNOWN_BRANDS.items():
        for brand in brands:
            if brand in name:
                features['brand'] = brand.replace(' ', '').replace('.', '')
                features['category'] = category
                break
        if features['brand']:
            break
    
    # Detectar modelo GPU
    gpu_match = re.search(GPU_PATTERN, name, re.IGNORECASE)
    if gpu_match:
        model = gpu_match.group(1)
        variant = gpu_match.group(2) if gpu_match.group(2) else ''
        features['model'] = f"rtx{model}" if 'rtx' in name or 'gtx' in name else f"rx{model}"
        features['variant'] = variant.lower() if variant else None
        features['category'] = 'gpu'
    
    # Detectar modelo CPU AMD
    cpu_amd_match = re.search(CPU_AMD_PATTERN, name, re.IGNORECASE)
    if cpu_amd_match:
        series = cpu_amd_match.group(1)
        model = cpu_amd_match.group(2)
        features['model'] = f"ryzen{series}_{model}"
        features['category'] = 'cpu'
    
    # Detectar modelo CPU Intel
    cpu_intel_match = re.search(CPU_INTEL_PATTERN, name, re.IGNORECASE)
    if cpu_intel_match:
        series = cpu_intel_match.group(1)
        model = cpu_intel_match.group(2)
        features['model'] = f"i{series}_{model}"
        features['category'] = 'cpu'
    
    # Detectar capacidade (RAM/Storage)
    capacity_match = re.search(RAM_CAPACITY_PATTERN, name, re.IGNORECASE)
    if capacity_match:
        size = capacity_match.group(1)
        ddr = capacity_match.group(2) if capacity_match.group(2) else ''
        features['capacity'] = f"{size}gb" + (f"_ddr{ddr}" if ddr else "")
        if not features['category']:
            features['category'] = 'ram' if ddr else 'storage'
    
    return features

def normalize_product_name(product_name, store=None):
    """
    Normaliza nome do produto para identificação consistente.
    
    Args:
        product_name (str): Nome completo do produto
        store (str, optional): Nome da loja
        
    Returns:
        str: Nome normalizado (usado como ID único)
        
    Exemplo:
        "Placa de Vídeo RTX 4060 ASUS Dual 8GB" → "asus_rtx4060_8gb"
        "ASUS RTX4060 Dual OC 8GB GDDR6" → "asus_rtx4060_8gb"
    """
    features = extract_features(product_name)
    
    # Montar tokens do nome normalizado
    tokens = []
    
    if features.get('brand'):
        tokens.append(features['brand'])
    
    if features.get('model'):
        tokens.append(features['model'])
    
    if features.get('variant'):
        tokens.append(features['variant'])
    
    if features.get('capacity'):
        tokens.append(features['capacity'])
    
    # Se não conseguiu extrair nada, usar estratégia de fallback
    if not tokens:
        # Limpar e tokenizar nome original
        name = product_name.lower()
        name = unidecode(name)
        # Remover stopwords
        words = name.split()
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        tokens = words[:4]  # Primeiras 4 palavras significativas
    
    # Criar nome normalizado
    normalized = '_'.join(tokens)
    
    # Limpar caracteres especiais
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    
    return normalized

def calculate_similarity(name1, name2):
    """
    Calcula similaridade entre dois nomes de produtos.
    
    Args:
        name1 (str): Primeiro nome
        name2 (str): Segundo nome
        
    Returns:
        float: Score de 0-100 (100 = idênticos)
    """
    norm1 = normalize_product_name(name1)
    norm2 = normalize_product_name(name2)
    
    # Se nomes normalizados são iguais, 100% similar
    if norm1 == norm2:
        return 100.0
    
    # Caso contrário, usar similaridade de tokens
    tokens1 = set(norm1.split('_'))
    tokens2 = set(norm2.split('_'))
    
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    
    if not union:
        return 0.0
    
    return (len(intersection) / len(union)) * 100.0

# Função auxiliar para testes
if __name__ == "__main__":
    test_cases = [
        "Placa de Vídeo RTX 4060 ASUS Dual 8GB",
        "ASUS GeForce RTX 4060 Dual OC 8GB GDDR6",
        "RTX 4060 8GB ASUS DUAL Edition",
        "Processador AMD Ryzen 5 5600",
        "AMD Ryzen 5 5600 3.5GHz 6-Core",
        "Memória RAM 16GB DDR4 3200MHz Kingston",
        "Kingston Fury 16GB DDR4 3200MHz",
    ]
    
    print("=== TESTE DE NORMALIZAÇÃO ===\n")
    for name in test_cases:
        normalized = normalize_product_name(name)
        features = extract_features(name)
        print(f"Original:    {name}")
        print(f"Normalizado: {normalized}")
        print(f"Features:    {features}")
        print()
