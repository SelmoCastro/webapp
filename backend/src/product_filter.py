# Lista de palavras que indicam produtos NÃO relacionados a hardware/PC
# Se o nome do produto contiver QUALQUER uma dessas palavras, será rejeitado
BLACKLIST_KEYWORDS = [
    # Produtos domésticos
    'panela', 'arroz', 'elétrica', 'cafeteira', 'café', 'xícara',
    'lençol', 'cama', 'colcha', 'travesseiro', 'edredom', 'fronha',
    'toalha', 'banho', 'mesa',
    
    # Bebidas e alimentos
    'cerveja', 'refrigerante', 'água', 'suco', 'vinho', 'whisky',
    'chocolate', 'biscoito', 'cereal', 'leite',
    
    # Roupas e acessórios
    'camisa', 'camiseta', 'calça', 'short', 'bermuda', 'sapato',
    'tênis', 'sandália', 'chinelo', 'boné', 'chapéu', 'bolsa',
    'mochila escolar', 'carteira',
    
    # Móveis
    'sofá', 'cadeira de escritório', 'estante', 'armário',
    'guarda-roupa', 'cômoda', 'criado-mudo',
    
    # Eletrodomésticos não relacionados
    'geladeira', 'freezer', 'micro-ondas', 'fogão', 'forno',
    'lavadora', 'secadora', 'aspirador', 'ventilador',
    'ar condicionado', 'aquecedor', 'umidificador',
    
    # Brinquedos e jogos físicos
    'boneca', 'carrinho', 'lego', 'bola', 'patinete',
    'bicicleta', 'triciclo',
    
    # Livros e papelaria
    'livro', 'caderno', 'agenda', 'caneta', 'lápis',
    
    # Beleza e higiene
    'shampoo', 'condicionador', 'sabonete', 'perfume',
    'desodorante', 'creme', 'loção',
    
    # Outros
    'pet', 'cachorro', 'gato', 'ração', 'aquário',
    'plantas', 'vaso', 'adubo', 'jardinagem',
    'fitness', 'musculação', 'yoga', 'bicicleta ergométrica'
]

# Lista de palavras que DEVEM estar presentes (whitelist - opcional)
# Se vazia, não aplica filtro positivo
WHITELIST_KEYWORDS = [
    # Hardware core
    'rtx', 'gtx', 'radeon', 'rx ', 'gpu', 'placa de vídeo', 'vga',
    'intel', 'amd', 'ryzen', 'core i', 'processador', 'cpu',
    'ddr3', 'ddr4', 'ddr5', 'memória', 'ram', 'Kingston', 'Corsair',
    'ssd', 'nvme', 'hd ', 'sata', 'armazenamento', 'disco',
    'motherboard', 'placa mãe', 'socket',
    'fonte', 'psu', 'power supply', 'w ', 'watt',
    
    # Periféricos PC
    'mouse', 'teclado', 'keyboard', 'headset', 'fone gamer',
    'mousepad', 'webcam', 'microfone gamer',
    
    # Componentes e acessórios
    'gabinete', 'case', 'cooler', 'ventoinha', 'water cooler',
    'pasta térmica', 'cabo sata', 'cabo hdmi', 'displayport',
    'monitor', 'led ', 'ips', 'hz', 'curved', 'ultrawide',
    
    # Notebook e portáteis
    'notebook', 'laptop', 'ultrabook', 'macbook',
    
    # Redes
    'roteador', 'modem', 'switch', 'access point', 'wi-fi',
]

def is_valid_pc_product(product_name):
    """
    Verifica se um produto é válido (relacionado a hardware/PC).
    
    Args:
        product_name (str): Nome do produto
        
    Returns:
        bool: True se for válido, False se deve ser rejeitado
    """
    name_lower = product_name.lower()
    
    # 1. Rejeitar se contiver palavras da blacklist
    for keyword in BLACKLIST_KEYWORDS:
        if keyword.lower() in name_lower:
            return False
    
    # 2. (Opcional) Aceitar apenas se contiver pelo menos uma palavra da whitelist
    # Comentado por padrão para não ser muito restritivo
    # if WHITELIST_KEYWORDS:
    #     has_valid_keyword = any(kw.lower() in name_lower for kw in WHITELIST_KEYWORDS)
    #     if not has_valid_keyword:
    #         return False
    
    return True
