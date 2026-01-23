import { useState, useEffect, useMemo } from 'react'
import { supabase } from './lib/supabase'
import ProductCard from './components/ProductCard'
import HistoryModal from './components/HistoryModal'
import Filters from './components/Filters'
import Dashboard from './components/Dashboard'
import { calculateTrend, isLowestPrice, categorizeProduct, isKit } from './utils/priceAnalytics'
import { LineChart, BarChart3, Package } from 'lucide-react'
import './App.css'

function App() {
  const [rawData, setRawData] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProductGroup, setSelectedProductGroup] = useState(null)
  const [activeTab, setActiveTab] = useState('products') // 'products' ou 'dashboard'

  // States para Filtros
  const [selectedStores, setSelectedStores] = useState(['Kabum', 'Pichau', 'Terabyte', 'Mercado Livre', 'Amazon', 'Magazine Luiza', 'Americanas'])
  const [selectedCategories, setSelectedCategories] = useState(['GPU', 'CPU', 'RAM', 'Motherboard', 'Storage', 'PSU', 'Outros'])

  useEffect(() => {
    fetchProducts()
  }, [])

  async function fetchProducts() {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('price_history')
        .select('*')
        .order('timestamp', { ascending: false })

      if (error) {
        console.error('Erro ao buscar produtos:', error)
      } else {
        setRawData(data || [])
      }
    } catch (e) {
      console.error('Erro inesperado:', e)
    } finally {
      setLoading(false)
    }
  }

  // Agrupar produtos duplicados (mesmo nome e loja) E Calcular Analytics
  const processedProducts = useMemo(() => {
    const groups = {}

    rawData.forEach(item => {
      // Usar normalized_name se disponível, senão fallback para product_name
      const productKey = item.normalized_name || item.product_name
      const key = `${item.store}-${productKey}`

      if (!groups[key]) {
        groups[key] = {
          product: item, // Mantém o item mais recente
          history: []
        }
      }
      groups[key].history.push(item)
    })

    // Retornar array dos produtos mais recentes com campos extras
    return Object.values(groups).map(g => {
      const history = g.history;
      const currentPrice = g.product.price;

      return {
        ...g.product,
        fullHistory: history,
        trend: calculateTrend(currentPrice, history),
        isLowestPrice: isLowestPrice(currentPrice, history),
        computedCategory: categorizeProduct(g.product.product_name),
        isKit: isKit(g.product.product_name)
      }
    })
  }, [rawData])



  const filteredProducts = processedProducts.filter(item => {
    const matchesSearch = item.product_name.toLowerCase().includes(searchTerm.toLowerCase());

    // Se nenhuma loja selecionada, mostrar TODAS. Senão, filtrar apenas as selecionadas
    const matchesStore = selectedStores.length === 0 ? true : selectedStores.includes(item.store);

    // Se nenhuma categoria selecionada, mostrar TODAS. Senão, filtrar apenas as selecionadas
    const matchesCategory = selectedCategories.length === 0 ? true : selectedCategories.includes(item.computedCategory);

    const hasValidPrice = item.price > 0; // Filtrar produtos sem preço

    return matchesSearch && matchesStore && matchesCategory && hasValidPrice;
  })

  return (
    <>
      <div className="header">
        <h1>PC Price Tracker 🖥️</h1>
        <p>Monitoramento de preços Kabum, Pichau e Terabyte</p>

        {/* Navigation Tabs */}
        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'products' ? 'active' : ''}`}
            onClick={() => setActiveTab('products')}
          >
            <Package size={20} />
            Produtos
          </button>
          <button
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <BarChart3 size={20} />
            Dashboard
          </button>
        </div>

        {activeTab === 'products' && (
          <input
            type="text"
            placeholder="Buscar produto..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        )}
      </div>

      {activeTab === 'dashboard' ? (
        <Dashboard products={processedProducts} />
      ) : (
        <div className="app-container">

          <Filters
            selectedStores={selectedStores}
            setSelectedStores={setSelectedStores}
            selectedCategories={selectedCategories}
            setSelectedCategories={setSelectedCategories}
          />

          <div className="main-content">
            {loading ? (
              <p>Carregando ofertas...</p>
            ) : (
              <div className="products-grid">
                {filteredProducts.length > 0 ? (
                  filteredProducts.map((product) => (
                    <div key={`${product.store}-${product.product_name}`} style={{ position: 'relative' }}>
                      <ProductCard product={product} />
                      <button
                        className="history-btn"
                        onClick={() => setSelectedProductGroup({ product, history: product.fullHistory })}
                        title="Ver Histórico"
                      >
                        <LineChart size={20} />
                      </button>
                    </div>
                  ))
                ) : (
                  <p>Nenhum produto encontrado.</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {selectedProductGroup && (
        <HistoryModal
          productGroup={selectedProductGroup}
          onClose={() => setSelectedProductGroup(null)}
        />
      )}
    </>
  )
}

export default App

