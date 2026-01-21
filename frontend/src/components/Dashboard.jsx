import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown, DollarSign, ShoppingCart, BarChart3, AlertCircle } from 'lucide-react';
import { analyzeCategoryTrends, getTopDeals } from '../utils/analytics';
import './Dashboard.css';

const Dashboard = ({ products }) => {
    const categoryTrends = useMemo(() => analyzeCategoryTrends(products), [products]);
    const topDeals = useMemo(() => getTopDeals(products, 5), [products]);

    // Estatísticas gerais
    const stats = useMemo(() => {
        const totalProducts = products.length;
        const dealsCount = products.filter(p => p.isLowestPrice).length;
        const avgPrice = products.length > 0 ? products.reduce((sum, p) => sum + p.price, 0) / products.length : 0;

        const risingCount = products.filter(p => p.trend?.direction === 'up').length;
        const fallingCount = products.filter(p => p.trend?.direction === 'down').length;

        return {
            totalProducts,
            dealsCount,
            avgPrice,
            risingCount,
            fallingCount,
            marketTrend: risingCount > fallingCount ? 'rising' : fallingCount > risingCount ? 'falling' : 'stable'
        };
    }, [products]);

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>Dashboard de Insights</h1>
                <p>Análise preditiva e tendências de mercado</p>
            </div>

            {/* KPIs Cards */}
            <div className="kpi-grid">
                <div className="kpi-card">
                    <div className="kpi-icon">
                        <BarChart3 size={24} />
                    </div>
                    <div className="kpi-content">
                        <span className="kpi-label">Produtos Monitorados</span>
                        <span className="kpi-value">{stats.totalProducts}</span>
                    </div>
                </div>

                <div className="kpi-card highlight">
                    <div className="kpi-icon">
                        <ShoppingCart size={24} />
                    </div>
                    <div className="kpi-content">
                        <span className="kpi-label">Oportunidades</span>
                        <span className="kpi-value">{stats.dealsCount}</span>
                    </div>
                </div>

                <div className="kpi-card">
                    <div className="kpi-icon">
                        <DollarSign size={24} />
                    </div>
                    <div className="kpi-content">
                        <span className="kpi-label">Preço Médio</span>
                        <span className="kpi-value">
                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(stats.avgPrice)}
                        </span>
                    </div>
                </div>

                <div className={`kpi-card ${stats.marketTrend === 'rising' ? 'danger' : stats.marketTrend === 'falling' ? 'success' : ''}`}>
                    <div className="kpi-icon">
                        {stats.marketTrend === 'rising' ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                    </div>
                    <div className="kpi-content">
                        <span className="kpi-label">Tendência Geral</span>
                        <span className="kpi-value">
                            {stats.marketTrend === 'rising' ? '📈 Subindo' : stats.marketTrend === 'falling' ? '📉 Caindo' : '➡️ Estável'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Tendências por Categoria */}
            <div className="section">
                <h2>Tendências por Categoria</h2>
                <div className="category-trends-grid">
                    {Object.entries(categoryTrends).map(([category, data]) => (
                        <div key={category} className={`category-card ${data.trending}`}>
                            <div className="category-header">
                                <h3>{category}</h3>
                                <span className={`trend-badge ${data.trending}`}>
                                    {data.trending === 'rising' ? '📈' : data.trending === 'falling' ? '📉' : '➡️'}
                                </span>
                            </div>
                            <div className="category-stats">
                                <div className="stat">
                                    <span className="stat-label">Produtos</span>
                                    <span className="stat-value">{data.products.length}</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-label">Média</span>
                                    <span className="stat-value">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(data.avgPrice)}
                                    </span>
                                </div>
                                <div className="stat">
                                    <span className="stat-label">Variação</span>
                                    <span className={`stat-value ${data.avgChange > 0 ? 'danger' : data.avgChange < 0 ? 'success' : ''}`}>
                                        {data.avgChange > 0 ? '+' : ''}{data.avgChange.toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                            <div className="category-recommendation">
                                {data.trending === 'falling' && (
                                    <p className="recommendation success">
                                        <AlertCircle size={16} />
                                        Aguarde! Preços em queda.
                                    </p>
                                )}
                                {data.trending === 'rising' && (
                                    <p className="recommendation danger">
                                        <AlertCircle size={16} />
                                        Compre logo! Preços subindo.
                                    </p>
                                )}
                                {data.trending === 'stable' && (
                                    <p className="recommendation info">
                                        <AlertCircle size={16} />
                                        Preços estáveis. Bom momento.
                                    </p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Top Oportunidades */}
            <div className="section">
                <h2>🔥 Melhores Oportunidades</h2>
                <div className="deals-list">
                    {topDeals.length > 0 ? (
                        topDeals.map(product => (
                            <div key={`${product.store}-${product.product_name}`} className="deal-item">
                                <div className="deal-info">
                                    <h4>{product.product_name}</h4>
                                    <span className="deal-store">{product.store}</span>
                                </div>
                                <div className="deal-price">
                                    <span className="price">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(product.price)}
                                    </span>
                                    {product.trend?.direction === 'down' && (
                                        <span className="price-drop">-{product.trend.percentage.toFixed(1)}%</span>
                                    )}
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="no-deals">Nenhuma oportunidade especial no momento. Continue monitorando!</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
