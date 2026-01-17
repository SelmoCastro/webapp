import React from 'react';
import { ExternalLink } from 'lucide-react';
import './ProductCard.css';

import TrendIndicator from './TrendIndicator';

const ProductCard = ({ product }) => {
    const { product_name, price, store, url, trend, isLowestPrice } = product;

    // Formatar preço
    const formattedPrice = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(price);

    return (
        <div className="product-card">
            {isLowestPrice && (
                <div className="opportunity-badge">
                    🔥 Menor Preço (30d)
                </div>
            )}
            <div className="card-header">
                <span className={`store-tag ${store.toLowerCase()}`}>{store}</span>
            </div>
            <div className="card-body">
                <h3 title={product_name}>{product_name}</h3>
                <div className="price-container">
                    <span className="price-label">À vista</span>
                    <span className="price-value">{formattedPrice}</span>
                    <TrendIndicator trend={trend} />
                </div>
            </div>
            <div className="card-footer">
                <a href={url} target="_blank" rel="noopener noreferrer" className="buy-button">
                    Ver na Loja <ExternalLink size={16} />
                </a>
            </div>
        </div>
    );
};

export default ProductCard;
