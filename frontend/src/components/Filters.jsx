import React from 'react';
import { Store, Cpu, HardDrive, MemoryStick, Zap, Package } from 'lucide-react';
import './Filters.css';

const Filters = ({ selectedStores, setSelectedStores, selectedCategories, setSelectedCategories }) => {
    const stores = ['Kabum', 'Pichau', 'Terabyte', 'Mercado Livre', 'Amazon'];
    const categories = [
        { name: 'GPU', icon: Package },
        { name: 'CPU', icon: Cpu },
        { name: 'RAM', icon: MemoryStick },
        { name: 'Motherboard', icon: HardDrive },
        { name: 'Storage', icon: HardDrive },
        { name: 'PSU', icon: Zap },
        { name: 'Outros', icon: Package }
    ];

    const toggleStore = (store) => {
        if (selectedStores.includes(store)) {
            setSelectedStores(selectedStores.filter(s => s !== store));
        } else {
            setSelectedStores([...selectedStores, store]);
        }
    };

    const toggleCategory = (cat) => {
        if (selectedCategories.includes(cat)) {
            setSelectedCategories(selectedCategories.filter(c => c !== cat));
        } else {
            setSelectedCategories([...selectedCategories, cat]);
        }
    };

    return (
        <aside className="filters-sidebar">
            <div className="sidebar-header">
                <Store size={20} />
                <h2>Filtros</h2>
            </div>

            <div className="filter-group">
                <h3>Lojas</h3>
                <div className="filter-options">
                    {stores.map(store => (
                        <label key={store} className="filter-toggle">
                            <input
                                type="checkbox"
                                checked={selectedStores.includes(store)}
                                onChange={() => toggleStore(store)}
                            />
                            <span className="toggle-slider"></span>
                            <span className="toggle-label">{store}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="filter-group">
                <h3>Categorias</h3>
                <div className="filter-options">
                    {categories.map(({ name, icon: Icon }) => (
                        <label key={name} className="filter-toggle">
                            <input
                                type="checkbox"
                                checked={selectedCategories.includes(name)}
                                onChange={() => toggleCategory(name)}
                            />
                            <span className="toggle-slider"></span>
                            <Icon size={16} className="category-icon" />
                            <span className="toggle-label">{name}</span>
                        </label>
                    ))}
                </div>
            </div>
        </aside>
    );
};

export default Filters;
