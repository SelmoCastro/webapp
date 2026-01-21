// Análise Preditiva de Preços

export function calculatePriceTrend(history) {
    if (!history || history.length < 3) return null;

    // Ordenar por timestamp
    const sorted = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const prices = sorted.map(h => h.price);

    // Regressão linear simples (y = mx + b)
    const n = prices.length;
    const xValues = Array.from({ length: n }, (_, i) => i);
    const yValues = prices;

    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = yValues.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Previsão para próximos 7 dias
    const futurePrice = slope * (n + 7) + intercept;

    // Confiança baseada em R²
    const yMean = sumY / n;
    const ssTotal = yValues.reduce((sum, y) => sum + Math.pow(y - yMean, 2), 0);
    const ssPred = yValues.map((y, i) => slope * i + intercept);
    const ssRes = yValues.reduce((sum, y, i) => sum + Math.pow(y - ssPred[i], 2), 0);
    const rSquared = 1 - (ssRes / ssTotal);

    return {
        currentPrice: prices[prices.length - 1],
        predictedPrice: futurePrice,
        trend: slope > 0 ? 'rising' : slope < 0 ? 'falling' : 'stable',
        changePercentage: ((futurePrice - prices[prices.length - 1]) / prices[prices.length - 1]) * 100,
        confidence: Math.max(0, Math.min(100, rSquared * 100)),
        volatility: calculateVolatility(prices)
    };
}

export function calculateVolatility(prices) {
    if (prices.length < 2) return 0;

    const mean = prices.reduce((a, b) => a + b, 0) / prices.length;
    const squaredDiffs = prices.map(price => Math.pow(price - mean, 2));
    const variance = squaredDiffs.reduce((a, b) => a + b, 0) / prices.length;
    const stdDev = Math.sqrt(variance);

    return (stdDev / mean) * 100; // Coeficiente de variação
}

export function getRecommendation(analysis) {
    if (!analysis) return { action: 'hold', reason: 'Dados insuficientes' };

    const { trend, changePercentage, volatility, confidence } = analysis;

    // Regras de negócio
    if (trend === 'falling' && changePercentage < -5 && confidence > 60) {
        return {
            action: 'wait',
            reason: 'Preço em queda. Aguarde para comprar mais barato.',
            color: 'warning'
        };
    }

    if (trend === 'rising' && changePercentage > 5 && confidence > 60) {
        return {
            action: 'buy-now',
            reason: 'Preço subindo. Compre agora antes que fique mais caro.',
            color: 'danger'
        };
    }

    if (volatility > 15) {
        return {
            action: 'hold',
            reason: 'Preço muito volátil. Monitore por mais alguns dias.',
            color: 'info'
        };
    }

    return {
        action: 'good-time',
        reason: 'Preço estável. Bom momento para comprar.',
        color: 'success'
    };
}

export function analyzeCategoryTrends(products) {
    const categoryData = {};

    products.forEach(product => {
        const category = product.computedCategory || 'Outros';

        if (!categoryData[category]) {
            categoryData[category] = {
                products: [],
                avgPrice: 0,
                avgChange: 0,
                trending: 'stable'
            };
        }

        if (product.trend && typeof product.trend === 'object') {
            categoryData[category].products.push(product);
        }
    });

    // Calcular estatísticas por categoria
    Object.keys(categoryData).forEach(category => {
        const prods = categoryData[category].products;
        if (prods.length === 0) return;

        const avgPrice = prods.reduce((sum, p) => sum + p.price, 0) / prods.length;
        const changes = prods.filter(p => p.trend?.percentage).map(p => p.trend.direction === 'up' ? p.trend.percentage : -p.trend.percentage);
        const avgChange = changes.length > 0 ? changes.reduce((a, b) => a + b, 0) / changes.length : 0;

        categoryData[category].avgPrice = avgPrice;
        categoryData[category].avgChange = avgChange;
        categoryData[category].trending = avgChange > 2 ? 'rising' : avgChange < -2 ? 'falling' : 'stable';
    });

    return categoryData;
}

export function getTopDeals(products, limit = 5) {
    return products
        .filter(p => p.isLowestPrice)
        .sort((a, b) => {
            // Priorizar produtos com maior queda de preço
            const trendA = a.trend?.direction === 'down' ? a.trend.percentage : 0;
            const trendB = b.trend?.direction === 'down' ? b.trend.percentage : 0;
            return trendB - trendA;
        })
        .slice(0, limit);
}
