import React from 'react';

const Filters = ({ selectedStores, setSelectedStores, selectedCategories, setSelectedCategories }) => {
    const stores = ['Kabum', 'Pichau', 'Terabyte'];
    const categories = ['GPU', 'CPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Outros'];

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
            <div className="filter-group">
                <h3>Lojas</h3>
                {stores.map(store => (
                    <label key={store} className="filter-option">
                        <input
                            type="checkbox"
                            checked={selectedStores.includes(store)}
                            onChange={() => toggleStore(store)}
                        />
                        {store}
                    </label>
                ))}
            </div>

            <div className="filter-group">
                <h3>Categorias</h3>
                {categories.map(cat => (
                    <label key={cat} className="filter-option">
                        <input
                            type="checkbox"
                            checked={selectedCategories.includes(cat)}
                            onChange={() => toggleCategory(cat)}
                        />
                        {cat}
                    </label>
                ))}
            </div>
        </aside>
    );
};

export default Filters;
