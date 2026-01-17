import React, { useMemo } from 'react';
import PriceHistoryChart from './PriceHistoryChart';
import './HistoryModal.css';
import { X } from 'lucide-react';

const HistoryModal = ({ productGroup, onClose }) => {
    const { product, history } = productGroup;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{product.product_name}</h2>
                    <button className="close-button" onClick={onClose}><X /></button>
                </div>

                <div className="modal-body">
                    <div className="chart-container">
                        <PriceHistoryChart history={history} />
                    </div>

                    <div className="history-table">
                        <h3>Últimos Registros</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Preço</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.slice().sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 5).map(item => (
                                    <tr key={item.id}>
                                        <td>{new Date(item.timestamp).toLocaleString('pt-BR')}</td>
                                        <td>R$ {item.price.toFixed(2)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HistoryModal;
