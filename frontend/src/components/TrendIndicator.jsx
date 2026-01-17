import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const TrendIndicator = ({ trend }) => {
    if (!trend || trend === 'stable') {
        return (
            <div className="trend-indicator stable" title="Preço estável">
                <Minus size={16} />
                <span>Estável</span>
            </div>
        );
    }

    const { direction, percentage } = trend;
    const isUp = direction === 'up';

    return (
        <div className={`trend-indicator ${direction}`} title={isUp ? 'Preço subiu' : 'Preço caiu'}>
            {isUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{percentage.toFixed(1)}%</span>
        </div>
    );
};

export default TrendIndicator;
