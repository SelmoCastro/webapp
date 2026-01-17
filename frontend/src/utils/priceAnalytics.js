export function calculateTrend(currentPrice, history) {
    if (!history || history.length < 2) return null;

    // Ordenar histórico por data (mais recente primeiro) se não estiver
    // Mas o App.jsx já manda ordenado pelo Supabase. Vamos assumir que sim ou ordenar por garantia.
    const sortedHistory = [...history].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // O índice 0 é o atual, o índice 1 é o anterior
    // Se o array history incluir o atual, pegamos o segundo. Se não, pegamos o primeiro.
    // No nosso App.jsx, 'history' é 'fullHistory' que inclui o item atual.

    // Procura o primeiro preço diferente do atual para comparar
    const previousEntry = sortedHistory.find(item => Math.abs(item.price - currentPrice) > 0.01);

    if (!previousEntry) return 'stable';

    const previousPrice = previousEntry.price;
    const diff = currentPrice - previousPrice;
    const percentage = (diff / previousPrice) * 100;

    if (diff > 0) return { direction: 'up', percentage: Math.abs(percentage) };
    if (diff < 0) return { direction: 'down', percentage: Math.abs(percentage) };
    return 'stable';
}

export function isLowestPrice(currentPrice, history) {
    if (!history || history.length === 0) return true;

    // Ignorar o próprio registro atual na comparação se ele estiver no histórico duplicado
    const otherPrices = history.filter(h => h.price !== currentPrice).map(h => h.price);
    if (otherPrices.length === 0) return true; // Se só tem ele, é o menor

    const minPrice = Math.min(...otherPrices);
    return currentPrice <= minPrice;
}

export function categorizeProduct(productName) {
    const name = productName.toLowerCase();

    // Prioridade para Placa-mãe (Para não cair em RAM DDR4)
    if (name.includes('placa mãe') || name.includes('placa-mãe') || name.includes('b550') || name.includes('b450') || name.includes('a520') || name.includes('motherboard') || name.includes('z690') || name.includes('z790')) return 'Motherboard';

    // Categorias padrão
    if (name.includes('rtx') || name.includes('rx 6') || name.includes('rx 7') || name.includes('geforce') || name.includes('radeon') || name.includes('placa de vídeo')) return 'GPU';
    if (name.includes('ryzen') || name.includes('core i') || name.includes('intel') || name.includes('processador')) return 'CPU';
    if (name.includes('ddr4') || name.includes('ddr5') || name.includes('memória')) return 'RAM';
    if (name.includes('ssd') || name.includes('nvme') || name.includes('hd') || name.includes('armazenamento')) return 'Storage';
    if (name.includes('fonte') || name.includes('w')) return 'PSU';
    return 'Outros';
}

export function isKit(productName) {
    const name = productName.toLowerCase();
    // Procura por padrões como: 2x, 2 x, 4x, kit
    if (name.includes('kit') || name.includes('2x') || name.includes('2 x') || name.includes('4x') || name.includes('4 x')) return true;
    return false;
}
