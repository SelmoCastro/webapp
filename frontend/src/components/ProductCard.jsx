import React from 'react';
import { ExternalLink } from 'lucide-react';
import './ProductCard.css';

const ProductCard = ({ product }) => {
    const { product_name, price, store, url } = product;

    // Formatar preço
    const formattedPrice = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(price);

    return (
        <div className="product-card">
            <div className="card-header">
                <span className={`store-tag ${store.toLowerCase()}`}>{store}</span>
            </div>
            <div className="card-body">
                <h3 title={product_name}>{product_name}</h3>
                <div className="price-container">
                    <span className="price-label">À vista</span>
                    <span className="price-value">{formattedPrice}</span>
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
